from typing import List
from pydantic import BaseModel, Field
from enum import Enum

class Checkpoint(BaseModel):
    id: str = Field(..., description="Unique identifier for the checkpoint")
    user_id: str = Field(..., description="Unique identifier for the user")
    file_id: str = Field(..., description="Unique identifier for the file")
    lesson_progress: str = Field(..., description="Current teaching progress")
    
    
