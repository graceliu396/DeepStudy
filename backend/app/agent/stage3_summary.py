import os
import json
import asyncio
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.functions import KernelArguments
import sys
from pathlib import Path
print(str(Path(__file__).parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent))
from app.core.kernel import kernel,load_prompt



QUESTION_RETRIEVAL_INSTRUCTIONS = load_prompt("stage3_quiz_generation")

SUMMARY_INSTRUCTIONS = load_prompt("stage3_summary")

SUMMARY_PROMPT = """
Here is the teaching script of this lesson:
{}

And here is the chat history between teacher and student:
{}
"""

QUIZ_PROMPT = """
Here is the teaching script of this lesson:
{}

And here is the summary of this lesson, you can generate 4-5 fill-in-the-blank questions based on student's weakness:
{}
"""

def parse_json_response(response):
    try:
        cleaned_content = response
        cleaned_content = cleaned_content.replace("[START]", "").replace("[END]", "")
        cleaned_content = cleaned_content.replace("```json", "").replace("```", "")
        cleaned_content = cleaned_content.strip()
        json_content = json.loads(cleaned_content)
        return json_content
    except json.JSONDecodeError:
        print("\nWarning: Unable to parse Planner's response as JSON format")

def parse_md_response(response):
    cleaned_content = response
    cleaned_content = cleaned_content.replace("[START]", "").replace("[END]", "")
    cleaned_content = cleaned_content.replace("```md", "").replace("```", "").replace("```markdown", "").replace("```Markdown", "")
    cleaned_content = cleaned_content.strip()
    return cleaned_content

# stage4 主流程

async def retrieve_questions(summary_content: dict, teaching_script: dict) -> dict:
    setting=kernel.get_prompt_execution_settings_from_service_id(service_id="azure_openai")
    setting.function_choice_behavior.NoneInvoke()
    question_generator=ChatCompletionAgent(
        kernel=kernel,
        name="question_generator",
        instructions=QUESTION_RETRIEVAL_INSTRUCTIONS,
        arguments=KernelArguments(settings=setting)
    )
    response=await question_generator.get_response(messages=QUIZ_PROMPT.format(teaching_script, summary_content))
    print(response.message.content)
    quiz=parse_json_response(response.message.content)
    print(quiz)
    quiz_without_ans=""
    questions=quiz["questions"]
    for question in questions:
        quiz_without_ans+=question['stem']
        quiz_without_ans+="\n"
        quiz_without_ans+=question['options']
        quiz_without_ans+="\n\n"
    return quiz_without_ans

async def generate_report(teaching_script: dict, chat_history: str) -> str:
    setting=kernel.get_prompt_execution_settings_from_service_id(service_id="azure_openai")
    setting.function_choice_behavior.NoneInvoke()
    generator=ChatCompletionAgent(
        kernel=kernel,
        name="summary_generator",
        instructions=SUMMARY_INSTRUCTIONS,
        arguments=KernelArguments(settings=setting)
    )
    response=await generator.get_response(messages=SUMMARY_PROMPT.format(teaching_script, chat_history))
    md_summary_content=parse_md_response(response.message.content)
    return md_summary_content


async def main():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        json_file_path = os.path.join(script_dir, 'teaching_script.json')
        txt_file_path = os.path.join(script_dir, "summary.txt")
        with open(json_file_path, 'r', encoding='utf-8') as f:
            teaching_script = json.load(f)
            formatted_script = json.dumps(teaching_script, ensure_ascii=False, indent=2)

        with open(txt_file_path, 'r', encoding='utf-8') as f:
            summary_content = f.read()

    except FileNotFoundError:
        print("Error: teaching_script.json file not found")
        return
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in teaching_script.json")
        return
    except Exception as e:
        print(f"Error occurred while reading file: {str(e)}")
        return
    
    response = await retrieve_questions(summary_content, teaching_script)
    print("Generated Report:")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())  