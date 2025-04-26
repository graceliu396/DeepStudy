from fastapi import APIRouter
from app.models.schema import LessonInput, LessonReport
from app.services.analyzer import analyze_weaknesses
from app.services.retriever import retrieve_questions
from app.services.grader import generate_report

router = APIRouter(prefix="/stage4", tags=["Stage4"])

@router.post("/process", response_model=LessonReport)
async def process_lesson(input_data: LessonInput):
    weaknesses = analyze_weaknesses(input_data)
    questions = retrieve_questions(input_data.Topic, weaknesses)
    report = generate_report(input_data, weaknesses, questions)
    return report
