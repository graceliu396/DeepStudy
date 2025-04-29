import os
import json
import asyncio
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from openai import AsyncOpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")

# 全局 kernel 实例
kernel = None

def _create_kernel() -> Kernel:
    global kernel
    if kernel is None:
        kernel = Kernel()
        chat_service = OpenAIChatCompletion(
            ai_model_id="gpt-4",
            async_client=AsyncOpenAI(
                api_key=OPENAI_API_KEY,
                base_url=OPENAI_API_BASE,
            ),
        )
        kernel.add_service(chat_service)
    return kernel

# Agent instructions
ANALYSIS_INSTRUCTIONS = """
你是一个教育测评专家。
你的任务是根据学生在本节课中的提问、回答、犯的错误，提炼出他们的知识薄弱点。

**要求**：
- 输出学生的知识薄弱点（准确、精炼）
- 列出至少三个具体的薄弱点
- 输出格式为JSON：

[START]
{
    "weaknesses": [
        {"topic": "知识点名称", "reason": "犯错/提问背后的原因"},
        ...
    ]
}
[END]
"""

QUESTION_RETRIEVAL_INSTRUCTIONS = """
你是一个教学题目出题专家。
你的任务是基于以下两个条件，为学生智能推荐配套的练习题目：

1. 学生的知识薄弱点如下：{weaknesses}
2. 本节课的教学内容如下：{teaching_script}

**要求**：
- 题目要精准对标学生弱点
- 至少生成3题
- 每题包括题目内容、选项、标准答案
- 输出格式为JSON：

[START]
{
    "questions": [
        {"question": "题目内容", "options": ["A", "B", "C", "D"], "answer": "B"},
        ...
    ]
}
[END]
"""

EXPLANATION_INSTRUCTIONS = """
你是一个教学讲解专家。
学生刚刚在以下题目中答错了，请你详细讲解错因，并帮助他们理解正确答案。

题目：{question}
学生答案：{student_answer}
正确答案：{correct_answer}

请用通俗易懂的语言解释为什么学生错了、为什么正确答案是对的。
可以使用比喻、例子、画图等方式。
输出格式为JSON：
[START]
{"explanation": "你的讲解内容..."}
[END]
"""

SUMMARY_INSTRUCTIONS = """
你是一个资深教学总结师。
你的任务是根据本节课的内容、学生课堂表现、作答情况，生成一个结构化的总结报告。

**总结报告需要包括**：
- 本节课教学重点
- 本节课教学难点
- 学生个人短板（结合上节课分析的弱点）
- 针对性的学习建议

**输出格式为JSON**：

[START]
{
    "summary": {
        "teaching_highlights": "",
        "teaching_difficulties": "",
        "student_weaknesses": [],
        "study_suggestions": ""
    }
}
[END]
"""

# 辅助函数：清理并解析JSON
def parse_agent_json(raw_content: str) -> dict:
    try:
        cleaned = raw_content.replace("[START]", "").replace("[END]", "").strip()
        return json.loads(cleaned)
    except Exception as e:
        raise ValueError(f"Failed to parse agent output: {e}")

# 主流程函数
async def analyze_weaknesses(chat_history: str) -> dict:
    agent = ChatCompletionAgent(kernel=_create_kernel(), name="WeaknessAnalyzer", instructions=ANALYSIS_INSTRUCTIONS)
    response = await agent.get_response(messages=chat_history)
    return parse_agent_json(response.content.content)

async def retrieve_questions(weaknesses: dict, teaching_script: dict) -> dict:
    instructions = QUESTION_RETRIEVAL_INSTRUCTIONS.format(
        weaknesses=json.dumps(weaknesses, ensure_ascii=False),
        teaching_script=json.dumps(teaching_script, ensure_ascii=False)
    )
    agent = ChatCompletionAgent(kernel=_create_kernel(), name="QuestionRetriever", instructions=instructions)
    response = await agent.get_response(messages="请根据上面的信息出题")
    return parse_agent_json(response.content.content)

async def explain_question_mistake(question: str, student_answer: str, correct_answer: str) -> str:
    instructions = EXPLANATION_INSTRUCTIONS.format(
        question=question,
        student_answer=student_answer,
        correct_answer=correct_answer
    )
    agent = ChatCompletionAgent(kernel=_create_kernel(), name="MistakeExplainer", instructions=instructions)
    response = await agent.get_response(messages="请开始讲解")
    return parse_agent_json(response.content.content)

async def generate_report(teaching_script: dict, chat_history: str, weaknesses: dict) -> dict:
    agent = ChatCompletionAgent(kernel=_create_kernel(), name="SummaryGenerator", instructions=SUMMARY_INSTRUCTIONS)
    combined_input = f"教学内容：{json.dumps(teaching_script, ensure_ascii=False)}\n学生表现：{chat_history}\n学生弱点：{json.dumps(weaknesses, ensure_ascii=False)}"
    response = await agent.get_response(messages=combined_input)
    return parse_agent_json(response.content.content)

# 串联主流程
task_history = []

async def full_practice_flow(chat_history: str, teaching_script: dict, student_answers: list) -> dict:
    try:
        weaknesses = await analyze_weaknesses(chat_history)
    except Exception as e:
        return {"error": f"分析知识薄弱点失败: {str(e)}"}

    try:
        questions = await retrieve_questions(weaknesses, teaching_script)
    except Exception as e:
        return {"error": f"出题失败: {str(e)}"}

    if len(student_answers) > len(questions["questions"]):
        return {"error": "学生答案数量多于题目数量，可能存在数据错误"}

    explanations = []
    for idx, (q, student_answer) in enumerate(zip(questions["questions"], student_answers)):
        if student_answer == "end practice":
            break
        try:
            if student_answer != q["answer"]:
                explanation = await explain_question_mistake(
                    q["question"], student_answer, q["answer"]
                )
                explanations.append({"question": q["question"], "explanation": explanation["explanation"]})
            else:
                explanations.append({"question": q["question"], "explanation": "答对了，继续加油！"})
        except Exception as e:
            explanations.append({"question": q["question"], "explanation": f"讲解失败: {str(e)}"})

    try:
        summary = await generate_report(teaching_script, chat_history, weaknesses)
    except Exception as e:
        return {"error": f"总结生成失败: {str(e)}"}

    return {
        "weaknesses": weaknesses,
        "questions": questions,
        "explanations": explanations,
        "summary": summary
    }

