import redis
import json
from uuid import uuid4
from pathlib import Path
import sys
from datetime import timedelta  
import time
sys.path.append(str(Path(__file__).parent.parent.parent))
from app.core.config import settings
from app.schemas.chatHistory import Step
from app.tools.azure_cosmos_db import file_container,chat_history_container
from typing import Optional
from enum import Enum

class LessonCache:
    def __init__(self):
        self.conn = redis.Redis(
            host=settings.AZURE_REDIS_HOST,
            port=6380,
            password=settings.AZURE_REDIS_KEY,
            ssl=True,
            decode_responses=True  
        )
        self.ttl = 3600 * 24 * 3  


    def create_session(self, user_id: str, file_id: str, total_lessons: int) -> str:
        session_id = f"session_{uuid4()}"
        
        with self.conn.pipeline() as pipe:
            pipe.hset(f"session:{session_id}", mapping={
                "user_id": user_id,
                "file_id": file_id,
                "current_lesson": 0,
                "total_lessons": total_lessons
            })
            
            pipe.expire(f"session:{session_id}", self.ttl)
            pipe.execute()
            
        return session_id
    
    def create_file_record_cache(self, data: dict):
        file_id = data['id']
        redis_key = f"file_upload:{file_id}"
        
        try:
            with self.conn.pipeline() as pipe:
                pipe.hset(redis_key, mapping={
                    "user_id": data['user_id'],
                    "subject": data['subject'],
                    "file_topic": data['file_topic'],
                    "grade": data['grade'],
                    "file_content": data['file_content'],
                    "total_lessons": data['total_lessons']
                })
                
                lesson_plan_json = json.dumps(data['lesson_plan'])
                # print(type(lesson_plan_json['lesson_sequence']))
                pipe.hset(redis_key, "lesson_plan", lesson_plan_json)
                
                pipe.expire(redis_key, self.ttl)
                pipe.execute()
            return True
        except Exception as e:
            print(f"Error saving to Redis: {str(e)}")
            return False

    def get_lesson_state(self, session_id: str, lesson_index: int) -> dict:
        base_key = f"session:{session_id}:lesson:{lesson_index}"
        
        with self.conn.pipeline() as pipe:
            pipe.hget(f"{base_key}:data", "script")
            pipe.hget(f"{base_key}:data", "summary")
            pipe.hget(f"{base_key}:data", "exercises")
            script, summary, exercises = pipe.execute()

        chat_data = {}
        for step in Step:  
            chat_key = f"{base_key}:chat_history:{step.value}"
            messages = self.conn.lrange(chat_key, 0, -1)
            chat_data[step.value] = [json.loads(msg) for msg in messages]

        return {
            "script": json.loads(script) if script else None,
            "summary": json.loads(summary) if summary else None,
            "exercises": json.loads(exercises) if exercises else [],
            "chat_history": chat_data }

    def get_chat_history(self, session_id: str, lesson_index: int) -> dict:
        
        base_key = f"session:{session_id}:lesson:{lesson_index}"
        chat_data = {}

        with self.conn.pipeline() as pipe:
            for step in Step:
                chat_key = f"{base_key}:chat_history:{step.value}"
                pipe.lrange(chat_key, 0, -1)
            
            raw_messages = pipe.execute()
        
        for step, messages in zip(Step, raw_messages):
            chat_data[step.value] = [json.loads(msg) for msg in messages]

        return chat_data
    

    def get_step_chat_history(
        self, 
        session_id: str, 
        lesson_index: int, 
        step: Enum 
    ) -> list:
        
        step_value = step.value if isinstance(step, Enum) else str(step)
        
        chat_key = f"session:{session_id}:lesson:{lesson_index}:chat_history:{step_value}"
        
        raw_messages = self.conn.lrange(chat_key, 0, -1)
        return [json.loads(msg) for msg in raw_messages] if raw_messages else []

    
    def get_file_record_cache(self, file_id: str) -> dict:
        redis_key = f"file_upload:{file_id}"
        return self.conn.hgetall(redis_key)
    

    def get_group_discussion(self, session_id: str, lesson_index: int) -> str:
        base_key = f"session:{session_id}:lesson:{lesson_index}"
        script=self.conn.hget(f"{base_key}:data", "script")
        return json.loads(script)['Group Discussion Questions']
        

    def update_teaching_script(self, session_id: str, lesson_script: dict):
        lesson_index = self.conn.hget(f"session:{session_id}", "current_lesson")
        base_key = f"session:{session_id}:lesson:{lesson_index}"
        # print(lesson_script)
        
        with self.conn.pipeline() as pipe:
            pipe.hset(f"{base_key}:data", "script", json.dumps(lesson_script))
            pipe.expire(f"session:{session_id}", self.ttl)
            pipe.expire(f"{base_key}:data", self.ttl)
            pipe.execute()

    def update_lesson_summary(self, session_id: str, summary: str):
        lesson_index = self.conn.hget(f"session:{session_id}", "current_lesson")
        base_key = f"session:{session_id}:lesson:{lesson_index}"

        with self.conn.pipeline() as pipe:
            pipe.hset(f"{base_key}:data", "summary", summary)
            pipe.expire(f"session:{session_id}", self.ttl)
            pipe.expire(f"{base_key}:data", self.ttl)
            pipe.execute()

    def update_lesson_exercises(self, session_id: str, exercises: dict):
        lesson_index = self.conn.hget(f"session:{session_id}", "current_lesson")
        base_key = f"session:{session_id}:lesson:{lesson_index}"

        with self.conn.pipeline() as pipe:
            pipe.hset(f"{base_key}:data", "exercises", json.dumps(exercises))
            pipe.expire(f"session:{session_id}", self.ttl)
            pipe.expire(f"{base_key}:data", self.ttl)
            pipe.execute()

    def start_new_lesson(self, session_id: str):
        with self.conn.pipeline() as pipe:
            pipe.hincrby(f"session:{session_id}", "current_lesson", 1)
            pipe.execute()
            
        current_lesson = self.conn.hget(f"session:{session_id}", "current_lesson")
        return int(current_lesson)

    def save_chat_history(self, session_id: str, messages: list, step_type: Step):
        if not isinstance(step_type, Step):
            raise ValueError(f"Invalid step type: {step_type}")
        
        lesson_index = self.conn.hget(f"session:{session_id}", "current_lesson")
        if not lesson_index:
            raise ValueError(f"Session {session_id} has no current_lesson")
        
        type_key = f"session:{session_id}:lesson:{lesson_index}:chat_history:{step_type.value}"
        print(type_key)

        serialized = [json.dumps(msg) for msg in messages]
        print(serialized)
        if serialized: 
            self.conn.rpush(type_key, *serialized)
            self.conn.expire(type_key, self.ttl) 

    def migrate_session_data(self, redis_session_id: str):
        session_key = f"session:{redis_session_id}"
        session_data = lesson_cache.conn.hgetall(session_key)
        
        cosmos_doc = {
            "session_id": redis_session_id,
            "type": "session",
            "user_id": session_data["user_id"],
            "file_id": session_data["file_id"],
            "currentLesson": int(session_data["current_lesson"]),
            "totalLessons": int(session_data["total_lessons"]),
            "lessons": []
        }
        
        for lesson_idx in range(cosmos_doc["totalLessons"]):
            lesson_data = lesson_cache.get_lesson_state(redis_session_id, lesson_idx)
            
            chat_history = {}
            for step_type in Step:
                key = step_type.value
                chat_history[key] = lesson_data["chat_history"].get(key, [])
            
            cosmos_doc["lessons"].append({
                "index": lesson_idx,
                "script": lesson_data["script"],
                "summary": lesson_data["summary"],
                "exercises": lesson_data["exercises"],
                "chatHistory": chat_history
            })
        
        chat_history_container.upsert_item(cosmos_doc)

    def migrate_file_data(self, file_id: str):
        redis_key = f"file_upload:{file_id}"
        file_data = lesson_cache.conn.hgetall(redis_key)
        
        cosmos_doc = {
            "id": file_id,
            "user_id": file_data["user_id"],
            "subject": file_data["subject"],
            "file_topic": file_data["file_topic"],
            "grade": file_data["grade"],
            "file_content": file_data["file_content"],
            "total_lessons": file_data["total_lessons"],
            "lesson_plan": json.loads(file_data["lesson_plan"])
        }
        
        file_container.upsert_item(cosmos_doc)


lesson_cache = LessonCache()


def test_lesson_flow():
    cache = LessonCache()
    
    
    state = cache.get_lesson_state("session_94f6b7de-011a-4142-9fd8-2406761a841c", 0)
    print("Lesson State:", state)
    

if __name__ == "__main__":
    test_lesson_flow()