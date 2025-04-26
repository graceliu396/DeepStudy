from app.models.schema import LessonInput, Weakness
from app.config import llm
import json
from typing import List

def analyze_weaknesses(lesson: LessonInput) -> List[Weakness]:
    conv_str = "\n".join([f"{c.Speaker}: {c.Text}" for c in lesson.ConversationHistory])
    prompt = f"""
You are a teaching assistant. Analyze this conversation and extract user weaknesses as JSON:
{{"Weaknesses":[{{"Topic":"...","Description":"...","Evidence":["...",...]}}]}}
Conversation:
{conv_str}
"""
    response = llm.invoke(prompt)
    return [Weakness(**w) for w in json.loads(response)['Weaknesses']]
