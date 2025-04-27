# Copyright (c) Microsoft. All rights reserved.
import os
import asyncio
import json
import time
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
from openai import AsyncOpenAI


PLANNER_NAME = "Planner"
PLANNER_INSTRUCTIONS = load_prompt("stage0_planner")

CHECKER_NAME = "Checker"
CHECKER_INSTRUCTIONS = load_prompt("stage0_expert")

TASK = """
{
    "Topic": "Apply and extend previous understandings of arithmetic to algebraic expressions.",
    "Student Age": "6th grade",
    "Humor Level": "Middle",
    "Teaching Style": "Socratic Questioning and examples",
    "Teaching Time": "20 minutes"
}
"""

async def generate_teaching_script(task: str):
    agent_planner = ChatCompletionAgent(
        kernel=kernel,
        name=PLANNER_NAME,
        instructions=PLANNER_INSTRUCTIONS,
    )

    agent_checker = ChatCompletionAgent(
        kernel=kernel,
        name=CHECKER_NAME,
        instructions=CHECKER_INSTRUCTIONS,
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
    asyncio.run(generate_teaching_script())