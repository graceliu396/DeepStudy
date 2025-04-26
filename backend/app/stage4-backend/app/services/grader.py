from app.models.schema import LessonInput, Weakness, Question, LessonReport
from app.config import llm
import json
from typing import List

def generate_report(lesson: LessonInput, weaknesses: List[Weakness], questions: List[Question]) -> LessonReport:
    prompt = f"""
Create a structured lesson report as JSON:
1.LessonTopic
2.KeyConcepts
3.ChallengingPoints
4.UserWeaknesses
5.RecommendedExercises
6.StudySuggestions
Input:
Topic: {lesson.Topic}
Summary: {lesson.Summary}
Weaknesses: {json.dumps([w.dict() for w in weaknesses], ensure_ascii=False)}
RecommendedQuestions: {json.dumps([q.dict() for q in questions], ensure_ascii=False)}
"""
    response = llm.invoke(prompt)
    return LessonReport(**json.loads(response))
