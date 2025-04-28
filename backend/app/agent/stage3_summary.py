# backend/app/agent/stage4/learning_analysis.py

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

def _create_kernel() -> Kernel:
    kernel = Kernel()
    chat_service = OpenAIChatCompletion(
        ai_model_id="gpt-4",  # 这里可以按需换成deepseek-chat或gpt-4
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
- 每题包括题目内容和标准答案
- 输出格式为JSON：

[START]
{
    "questions": [
        {"question": "题目内容", "answer": "标准答案"},
        ...
    ]
}
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

# stage4 主流程

async def analyze_weaknesses(chat_history: str) -> dict:
    kernel = _create_kernel()
    agent = ChatCompletionAgent(kernel=kernel, name="WeaknessAnalyzer", instructions=ANALYSIS_INSTRUCTIONS)
    response = await agent.get_response(messages=chat_history)
    return parse_agent_json(response.content.content)

async def retrieve_questions(weaknesses: dict, teaching_script: dict) -> dict:
    kernel = _create_kernel()
    instructions = QUESTION_RETRIEVAL_INSTRUCTIONS.format(
        weaknesses=json.dumps(weaknesses, ensure_ascii=False),
        teaching_script=json.dumps(teaching_script, ensure_ascii=False)
    )
    agent = ChatCompletionAgent(kernel=kernel, name="QuestionRetriever", instructions=instructions)
    response = await agent.get_response(messages="请根据上面的信息出题")
    return parse_agent_json(response.content.content)

async def generate_report(teaching_script: dict, chat_history: str, weaknesses: dict) -> dict:
    kernel = _create_kernel()
    agent = ChatCompletionAgent(kernel=kernel, name="SummaryGenerator", instructions=SUMMARY_INSTRUCTIONS)
    combined_input = f"教学内容：{json.dumps(teaching_script, ensure_ascii=False)}\n学生表现：{_
