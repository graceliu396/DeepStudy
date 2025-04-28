# Copyright (c) Microsoft. All rights reserved.
import os
import asyncio
import json
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from openai import AsyncOpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()
DEEPSEEK_API_KEY = os.getenv("OPENAI_API_KEY")

def _create_kernel_with_chat_completion() -> Kernel:
    kernel = Kernel()
    chat_service = OpenAIChatCompletion(
        ai_model_id="deepseek-chat",  
        async_client=AsyncOpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=os.getenv("OPENAI_API_BASE"),
        ),
    )
    kernel.add_service(chat_service)
    return kernel

TEACHER_NAME = "Teacher"
TEACHER_INSTRUCTIONS = """
你要完成角色扮演，扮演一个数学老师，给学生上课。
你面向的学生是K-12的学生，你要使用Socratic questioning method和Engaging teaching style。

**Rules**:
- 你只需要和学生对话，你说一句学生说一句，不要自己说太多。
- 你只需要输出要和学生说的内容，其余的内容不要输出。
- While you should try to answer student questions, you may ignore irrelevant questions and continue with the lesson.
- Use simple, clear language and avoid overly technical terms in your teaching.
- Maintain an engaging and interactive teaching style.
- Keep the lesson focused and on track according to the teaching script.
"""

CHECKER_NAME = "Checker"
CHECKER_INSTRUCTIONS = """
You are an experienced educator with ten years of teaching experience, known for your Socratic questioning method and engaging teaching style.
You have a talent for using humor and vivid examples to make complex concepts accessible to students.

*Task*: 你的任务是观察老师和学生的课堂对话，并且根据teaching script检查老师此轮的对话。

**Rules**:
- 你的输入是老师和学生的对话内容和老师上课参考的teaching script。
- 你的输出是经过你检查、修改后老师应该说的话。
- 你要检查老师此时上课的进度，并且保证老师正在按照teaching script推进，避免突然跳跃。
"""

TASK = """
现在你是老师，我是学生，课堂上只有你和我两个人，你要和我对话，完成教学任务。
"""

CHECKER_TASK = """
这是老师和学生的历史对话：
{}

这里是老师接下来要说的内容：
{}

请根据teaching script检查修改老师此轮的对话。
"""

def parse_checker_response(response):
    print(response)
    print(type(response))
    try:
        # 清理内容中的特殊标记
        cleaned_content = response
        # 移除 [START] 和 [END] 标记
        cleaned_content = cleaned_content.replace("[START]", "").replace("[END]", "")
        # 移除可能的 ```json 和 ``` 标记
        cleaned_content = cleaned_content.replace("```json", "").replace("```", "")
        # 清理前后的空白字符
        cleaned_content = cleaned_content.strip()
        
        # 尝试解析 JSON 内容
        json_content = json.loads(cleaned_content)
        return json_content
    except json.JSONDecodeError:
        print("\nWarning: Unable to parse Planner's response as JSON format")
    except Exception as e:
        print(f"\nError occurred while saving file: {str(e)}")

async def main():
    # 读取 teaching_script.json 文件
    try:
        with open('teaching_script.json', 'r', encoding='utf-8') as f:
            teaching_script = json.load(f)
            # 将 JSON 转换为格式化的字符串
            formatted_script = json.dumps(teaching_script, ensure_ascii=False, indent=2)
            # 更新 TASK 内容
            teacher_instructions = TEACHER_INSTRUCTIONS.format(formatted_script)
            checker_instructions = CHECKER_INSTRUCTIONS.format(formatted_script)
    except FileNotFoundError:
        print("Error: teaching_script.json file not found")
        return
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in teaching_script.json")
        return
    except Exception as e:
        print(f"Error occurred while reading file: {str(e)}")
        return

    kernel=_create_kernel_with_chat_completion()
    # 1. Create the reviewer agent based on the chat completion service
    agent_teacher = ChatCompletionAgent(
        kernel=kernel,
        name=TEACHER_NAME,
        instructions=teacher_instructions,
    )
    agent_checker = ChatCompletionAgent(
        kernel=kernel,
        name=CHECKER_NAME,
        instructions=checker_instructions,
    )

    print(f"Class begins!")
    is_completed = False
    is_reset = True
    chat_history = None
    while not is_completed:
        if is_reset:
            is_reset = False
            chat_history =""
            del agent_teacher
            agent_teacher = ChatCompletionAgent(
                kernel=kernel,
                name=TEACHER_NAME,
                instructions=teacher_instructions,
            )
            response = await agent_teacher.get_response(messages=TASK)
            checker_response = await agent_checker.get_response(messages=CHECKER_TASK.format(chat_history, response.content.content))
            checker_response = parse_checker_response(checker_response.content.content)["response"]
            print(f"# {TEACHER_NAME}: {checker_response}")
            chat_history+=f"# {TEACHER_NAME}: {checker_response}\n"
            


        user_input = input("Student: ").strip()
        print(f"# Student: {user_input}")
        chat_history+=f"# Student: {user_input}\n"
        print("================")

        if user_input.lower() == "exit":
            is_completed = True
            print("Class ends!")
            break
        if user_input.lower() == "reset":
            print("Class reset!")
            is_reset = True
            continue

        response = await agent_teacher.get_response(messages=user_input)
        checker_response = await agent_checker.get_response(messages=CHECKER_TASK.format(chat_history, response.content.content))
        checker_response = parse_checker_response(checker_response.content.content)["response"]
        print(f"# {TEACHER_NAME}: {checker_response}")
        chat_history+=f"# {TEACHER_NAME}: {checker_response}\n"
        is_reset = False

if __name__ == "__main__":
    asyncio.run(main())
