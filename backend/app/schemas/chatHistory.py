from typing import List
from pydantic import BaseModel, Field
from enum import Enum

class Step(str, Enum):
    TEACHING = "teaching"
    GROUP_DISCUSSION = "group_discussion"
    FINAL_SUMMARY = "final_summary"
    PRACTICE = "practice"


class ChatHistory(BaseModel):
    step: Step = Field(..., description="Step of the chat history")
    history: List[dict] = Field(..., description="Chat history")

class ChatHistorys(BaseModel):
    id: str = Field(..., description="Unique identifier for the chat history")
    user_id: str = Field(..., description="Unique identifier for the user")
    file_id: str = Field(..., description="Unique identifier for the file")
    session_id: str = Field(..., description="Unique identifier for the session")
    history: List[ChatHistory] = Field(..., description="Chat history")

    
    
