from typing import List
from pydantic import BaseModel, Field
from enum import Enum

# 定义可选的 Grade 等级
class Grade(str, Enum):
    K = "K"
    GRADE_1 = "1"
    GRADE_2 = "2"
    GRADE_3 = "3"
    GRADE_4 = "4"
    GRADE_5 = "5"
    GRADE_6 = "6"
    GRADE_7 = "7"
    GRADE_8 = "8"
    H = "H"

# 定义返回的数据结构
class MiniLesson(BaseModel):
    mini_lesson_id: int = Field(..., description="Unique identifier for the lesson")
    mini_lesson_title: str = Field(..., description="Concise title capturing the mini-lesson focus (e.g., 'Understanding Multiplication as Equal Groups')")
    key_concepts: List[str] = Field(..., description="Key learning points students should master for this mini-lesson")

class Plan(BaseModel):
    subject: str = Field(..., description="Subject of the uploaded file (e.g., Math, Science, Art, etc.)")
    topic: str = Field(..., description="Broad mathematical domain (e.g., Operations & Algebraic Thinking)")
    grade: Grade = Field(..., description="The target students' grade level (K, 1-8, or H)")
    lesson_sequence: List[MiniLesson] = Field(..., description="Ordered series of mini-lessons")


class FileUpload(BaseModel):
    id: str = Field(..., description="Unique identifier for the file")
    user_id: str = Field(..., description="Unique identifier for the user")
    subject: str = Field(..., description="Subject of the uploaded file")
    file_topic: str = Field(..., description="Topic of the uploaded file")
    grade: Grade = Field(..., description="The target students' grade level (K, 1-8, or H)")
    file_content: str = Field(..., description="Content of the uploaded file")
    lesson_plan: Plan = Field(..., description="Lesson plan for the uploaded file")
    total_lessons: int = Field(..., description="Total number of mini-lessons")
    
