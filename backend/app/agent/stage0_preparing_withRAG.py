# Copyright (c) Microsoft. All rights reserved.
import os
import asyncio
import json
import time
import sys
from pathlib import Path
print(str(Path(__file__).parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent))
from app.core.kernel import kernel, load_prompt
from semantic_kernel.agents import AgentGroupChat, ChatCompletionAgent, AzureAssistantAgent
from semantic_kernel.agents.strategies import TerminationStrategy
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.functions import KernelFunctionFromPrompt
from semantic_kernel.contents import ChatHistoryTruncationReducer
from semantic_kernel.agents.strategies import (
    KernelFunctionSelectionStrategy,
    KernelFunctionTerminationStrategy,
)
from semantic_kernel.functions import kernel_function
from serpapi import GoogleSearch
from app.core.config import settings
from app.agent.rag import *
from semantic_kernel.functions import KernelArguments


@kernel_function(
    name="web_search_tool",
    description="Performs online searches using a third-party API provider"
)
def fetch_web_results(search_term: str, region: str = "us", result_count: int = 2) -> str:
    """Retrieves search results from the web for a given query."""
    
    api_parameters = {
        "engine": "google",
        "q": search_term,
        "location": region,
        "api_key": settings.SERPAPI_KEY,
        "num": result_count,
    }
    
    response = GoogleSearch(api_parameters).get_dict()
    search_results = response.get("organic_results", [])
    
    if not search_results:
        return "No matching results available."
        
    formatted_output = []
    for idx, item in enumerate(search_results):
        title = item.get("title", "Untitled")
        description = item.get("snippet", "No description available")
        formatted_output.append(f"{idx+1}. {title} - {description}")
        
    return "\n".join(formatted_output)

@kernel_function(
    name="file_search_tool",
    description="Provide The Common Standards of USA for K12 students' mathematical learning."
)
def fetch_file_contents(query:str) -> str:
    """Retrieves search results from the file storage."""
    return answer_query(query)
    
kernel.add_functions(
    plugin_name="SearchAssistant",
    functions=[
        fetch_file_contents,
        fetch_web_results
    ]
)


PLANNER_NAME = "Planner"
PLANNER_INSTRUCTIONS = load_prompt("stage0_planner")

CHECKER_NAME = "Checker"
CHECKER_INSTRUCTIONS = load_prompt("stage0_expert")

EXAMPLE_TASK = """
{
    "mini_lesson_id": 1,
    "mini_lesson_title": "Understanding Multiplication as Equal Groups",
    "key_concepts": [
        "Interpret products as total objects in equal groups (e.g., 5 × 7 means 5 groups of 7)",
        "Create real-world contexts for multiplication expressions",
        "Use arrays/drawings to represent multiplication scenarios"
    ],
    "Student Age": "3th grade"
}
"""

async def generate_teaching_script_RAG(task: str):
    setting_planner=kernel.get_prompt_execution_settings_from_service_id(service_id="azure_openai")
    setting_planner.function_choice_behavior.Auto()
    agent_planner = ChatCompletionAgent(
        kernel=kernel,
        name=PLANNER_NAME,
        instructions=PLANNER_INSTRUCTIONS,
        arguments=KernelArguments(settings=setting_planner)
    )

    setting_checker=kernel.get_prompt_execution_settings_from_service_id(service_id="azure_openai")
    setting_checker.function_choice_behavior.NoneInvoke()
    agent_checker = ChatCompletionAgent(
        kernel=kernel,
        name=CHECKER_NAME,
        instructions=CHECKER_INSTRUCTIONS,
        arguments=KernelArguments(settings=setting_checker)
    )

    # 用于存储最后一次 Planner 的回答
    last_planner_response = None

    selection_function = KernelFunctionFromPrompt(
        function_name="selection",
        prompt=f"""
Examine the provided RESPONSE and choose the next participant.
State only the name of the chosen participant without explanation.
Never choose the participant named in the RESPONSE.

Choose only from these participants:
- {PLANNER_NAME}
- {CHECKER_NAME}

Rules:
- If RESPONSE is user input, it is {PLANNER_NAME}'s turn.
- If RESPONSE is by {PLANNER_NAME}, it is {CHECKER_NAME}'s turn.
- If RESPONSE is by {CHECKER_NAME}, it is {PLANNER_NAME}'s turn.

RESPONSE:
{{{{$lastmessage}}}}
""",
    )

    # 添加一个包装函数来打印选择结果
    def selection_result_parser(result):
        selected_agent = str(result.value[0]).strip() if result.value[0] is not None else PLANNER_NAME
        print(f"\nNext agent: {selected_agent}")
        return selected_agent
    
    def termination_result_parser(result):
        termination_keyword = "approved"
        return termination_keyword in str(result.value[0]).strip().lower()

    termination_keyword = "approved"

    termination_function = KernelFunctionFromPrompt(
        function_name="termination",
        prompt=f"""
Examine the RESPONSE from the Checker and determine whether to continue or terminate the conversation.

Rules:
1. If the Checker's response contains specific suggestions (in JSON format with "Suggestions" array), continue the conversation.
2. If the Checker's response is empty, contains no suggestions, or only contains "approved", you should also respond with "approved".

RESPONSE:
{{{{$lastmessage}}}}
""",
    )
    history_reducer = ChatHistoryTruncationReducer(target_count=5)
    # 3. Place the agents in a group chat with a custom termination strategy
    group_chat = AgentGroupChat(
        agents=[agent_planner, agent_checker],
        selection_strategy=KernelFunctionSelectionStrategy(
            kernel=kernel,
            function=selection_function,
            initial_agent=agent_planner,
            result_parser=selection_result_parser,  
            history_variable_name="lastmessage",
            history_reducer=history_reducer,
        ),
        termination_strategy=KernelFunctionTerminationStrategy(
            kernel=kernel,
            agents=[agent_checker],
            function=termination_function,
            result_parser=termination_result_parser,
            history_variable_name="lastmessage",
            maximum_iterations=10,
            history_reducer=history_reducer,
        ),
    )

   
    await group_chat.add_chat_message(message=task)
    print(f"# User: {task}")
    
    # 5. Invoke the chat
    async for content in group_chat.invoke():
        print("----------------------------------------------------------------")
        print(f"# {content.name}: {content.content}")
        # 保存 Planner 的回答
        if content.name == PLANNER_NAME:
            last_planner_response = content.content
        
        if last_planner_response is None:
            break
    # 保存最后一次 Planner 的回答到文件
    if last_planner_response:
        try:
            # 清理内容中的特殊标记
            cleaned_content = last_planner_response
            # 移除 [START] 和 [END] 标记
            cleaned_content = cleaned_content.replace("[START]", "").replace("[END]", "")
            # 移除可能的 ```json 和 ``` 标记
            cleaned_content = cleaned_content.replace("```json", "").replace("```", "")
            # 清理前后的空白字符
            cleaned_content = cleaned_content.strip()
            
            # 尝试解析 JSON 内容
            json_content = json.loads(cleaned_content)
            # with open('teaching_script.json', 'w', encoding='utf-8') as f:
            #     json.dump(json_content, f, ensure_ascii=False, indent=2)
            print("\nTeaching script has been saved to teaching_script.json")
            #print("===================")
            #print(json_content)
            return json_content
        except json.JSONDecodeError:
            print("\nWarning: Unable to parse Planner's response as JSON format")
        except Exception as e:
            print(f"\nError occurred while saving file: {str(e)}")


if __name__ == "__main__":
    asyncio.run(generate_teaching_script_RAG(EXAMPLE_TASK))