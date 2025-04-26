from pydantic import BaseModel
from typing import List, Dict

class ConversationEntry(BaseModel):
    Speaker: str
    Text: str

class LessonInput(BaseModel):
    Topic: str
    Summary: str
    ConversationHistory: List[ConversationEntry]

class Question(BaseModel):
    Question: str
    Options: Dict[str, str]
    Answer: str
    Explanation: str

class Weakness(BaseModel):
    Topic: str
    Description: str
    Evidence: List[str]

class LessonReport(BaseModel):
    LessonTopic: str
    KeyConcepts: List[str]
    ChallengingPoints: List[str]
    UserWeaknesses: List[Weakness]
    RecommendedExercises: List[Question]
    StudySuggestions: List[str]
