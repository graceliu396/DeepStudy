# Copyright (c) Microsoft. All rights reserved.
import os
import asyncio
import json
import time
import sys
import requests
import hashlib
from pathlib import Path
print(str(Path(__file__).parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent))
from app.core.kernel import kernel, load_prompt
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from app.core.kernel import kernel
from semantic_kernel.functions import KernelArguments
from app.tools.plugins import Dalle3Plugin
from app.schemas.chatHistory import Step
from app.tools.azure_redis_for_cache import lesson_cache


TEACHER_NAME = "Teacher"

TASK = """
Now you will play the role of the teacher and I'll be the student. 
In this classroom, it's just you and me. Please conduct the lesson according to the teaching script.
"""

TEACHER_TASK = """
Historical dialogue between teacher and student:
{}

Teaching script:
{}

Please review and decide the teacher's response according to the teaching script.
"""

def parse_response(response):
    print(response)
    print(type(response))
    try:
        cleaned_content = response
        cleaned_content = cleaned_content.replace("[START]", "").replace("[END]", "")
        cleaned_content = cleaned_content.replace("```json", "").replace("```", "")
        cleaned_content = cleaned_content.strip()
        json_content = json.loads(cleaned_content)
        return json_content
    except json.JSONDecodeError:
        print("\nWarning: Unable to parse Planner's response as JSON format")
    except Exception as e:
        print(f"\nError occurred while saving file: {str(e)}")


async def ws_class_begin(student_msg:str, session_id:str, lesson_index: int):
    
    script=lesson_cache.get_lesson_state(session_id, lesson_index)['script']
    teacher_instructions = load_prompt("stage1_teacher")
    chat_history=lesson_cache.get_step_chat_history(session_id, lesson_index, Step.TEACHING)
    current_msg= {"role": "student", "content": student_msg}
    chat_history.append(current_msg)

    chat_history_for_prompt=""
    for msg_dict in chat_history:
        msg_str=msg_dict["role"]+": "+msg_dict["content"]+"\n"
        chat_history_for_prompt+=msg_str

    setting=kernel.get_prompt_execution_settings_from_service_id(service_id="azure_openai")
    setting.function_choice_behavior.Auto()
    plugin=Dalle3Plugin()
    agent_teacher = ChatCompletionAgent(
        kernel=kernel,
        name=TEACHER_NAME,
        instructions=teacher_instructions,
        arguments=KernelArguments(settings=setting)
    )

    response = await agent_teacher.get_response(messages=TEACHER_TASK.format(chat_history_for_prompt, script))
    response = parse_response(response.message.content)
    teacher_msg=response['response']
    chat_history.append({"role": "teacher", "content": teacher_msg})
    lesson_cache.save_chat_history(session_id, chat_history, Step.TEACHING)


    if response["need_image"].lower()=="yes":
        prompt=response['image_prompt']
        url=plugin.generate_image_with_dalle3(prompt)

        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()  

            filename_hash = hashlib.md5(prompt.encode()).hexdigest()[:8]
            safe_prompt = "".join([c if c.isalnum() else "_" for c in prompt])
            filename = f"static/images/{safe_prompt[:20]}_{filename_hash}.jpg"
            
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            image_url = f"/static/images/{os.path.basename(filename)}"
        except Exception as e:
            print(f"Error generating image: {e}")
            image_url = None
    else:
        image_url = None

    return {
        "teacher_msg": teacher_msg,
        "image_url": image_url
    }
        
        

async def class_begin():
    # 读取 teaching_script.json 文件
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, 'teaching_script.json')
        with open(file_path, 'r', encoding='utf-8') as f:
            teaching_script = json.load(f)
            formatted_script = json.dumps(teaching_script, ensure_ascii=False, indent=2)
            teacher_instructions = load_prompt("stage1_teacher")
    except FileNotFoundError:
        print("Error: teaching_script.json file not found")
        return
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in teaching_script.json")
        return
    except Exception as e:
        print(f"Error occurred while reading file: {str(e)}")
        return

    setting=kernel.get_prompt_execution_settings_from_service_id(service_id="azure_openai")
    setting.function_choice_behavior.Auto()
    agent_teacher = ChatCompletionAgent(
        kernel=kernel,
        name=TEACHER_NAME,
        instructions=teacher_instructions,
        arguments=KernelArguments(settings=setting)
    )

    plugin=Dalle3Plugin()
    print(f"Class begins!")
    is_completed = False
    is_reset = True
    chat_history = None
    while not is_completed:
        if is_reset:
            is_reset = False
            chat_history ="# Student: Let's begin the class!\n"
            response = await agent_teacher.get_response(messages=TEACHER_TASK.format(chat_history, formatted_script))
            response = parse_response(response.message.content)
            if response["need_image"].lower()=="yes":
                prompt=response['image_prompt']
                url=plugin.generate_image_with_dalle3(prompt)
                print(f"# {TEACHER_NAME}: {response['response']}\n"+url)
            else:
                print(f"# {TEACHER_NAME}: {response["response"]}")
            chat_history+=f"# Teacher: {response['response']}\n"
            


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

        response = await agent_teacher.get_response(messages=TEACHER_TASK.format(chat_history, formatted_script))
        response = parse_response(response.message.content)
        if response["need_image"].lower()=="yes":
            prompt=response['image_prompt']
            url=plugin.generate_image_with_dalle3(prompt)
            print(f"# {TEACHER_NAME}: {response["response"]}\n"+url)
        else:
            print(f"# {TEACHER_NAME}: {response["response"]}")
        chat_history+=f"# Teacher: {response["response"]}\n"
        is_reset = False
    

if __name__ == "__main__":
    asyncio.run(class_begin())