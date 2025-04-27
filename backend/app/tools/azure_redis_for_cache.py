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

class LessonCache:
    def __init__(self):
        self.conn = redis.Redis(
            host=settings.AZURE_REDIS_HOST,
            port=6380,
            password=settings.AZURE_REDIS_KEY,
            ssl=True,
            decode_responses=True  # 自动解码返回数据
        )
        self.ttl = 3600 * 24 * 3  # 缓存保留3天


    def create_session(self, user_id: str, file_id: str, total_lessons: int) -> str:
        """创建新的学习会话"""
        session_id = f"session_{uuid4()}"
        
        # 使用pipeline批量操作
        with self.conn.pipeline() as pipe:
            # 存储会话数据
            pipe.hset(f"session:{session_id}", mapping={
                "user_id": user_id,
                "file_id": file_id,
                "current_lesson": 0,
                "total_lessons": total_lessons
            })
            
            # 设置TTL
            pipe.expire(f"session:{session_id}", self.ttl)
            pipe.execute()
            
        return session_id
    
    def create_file_record_cache(self, data: dict):
        """将文件记录存储到Redis"""
        file_id = data['id']
        redis_key = f"file_upload:{file_id}"
        
        try:
            # 使用pipeline批量操作
            with self.conn.pipeline() as pipe:
                # 基础字段直接存储
                pipe.hset(redis_key, mapping={
                    "user_id": data['user_id'],
                    "subject": data['subject'],
                    "file_topic": data['file_topic'],
                    "grade": data['grade'],
                    "file_content": data['file_content'],
                    "total_lessons": data['total_lessons']
                })
                
                # 处理嵌套的lesson_plan结构
                lesson_plan_json = json.dumps(data['lesson_plan'])
                # print(type(lesson_plan_json['lesson_sequence']))
                pipe.hset(redis_key, "lesson_plan", lesson_plan_json)
                
                # 设置TTL（例如7天过期）
                pipe.expire(redis_key, self.ttl)
                pipe.execute()
            return True
        except Exception as e:
            print(f"Error saving to Redis: {str(e)}")
            return False

    def get_lesson_state(self, session_id: str, lesson_index: int) -> dict:
        """获取指定课程的状态（修复版）"""
        base_key = f"session:{session_id}:lesson:{lesson_index}"
        
        # 获取脚本、总结、练习数据（哈希表操作）
        with self.conn.pipeline() as pipe:
            # 哈希表数据：script/summary/exercises
            pipe.hget(f"{base_key}:data", "script")
            pipe.hget(f"{base_key}:data", "summary")
            pipe.hget(f"{base_key}:data", "exercises")
            script, summary, exercises = pipe.execute()

        # 获取聊天记录（列表操作）
        chat_data = {}
        for step in Step:  # 遍历所有聊天类型
            chat_key = f"{base_key}:chat_history:{step.value}"
            # 使用LRANGE获取整个列表
            messages = self.conn.lrange(chat_key, 0, -1)
            chat_data[step.value] = [json.loads(msg) for msg in messages]

        return {
            "script": json.loads(script) if script else None,
            "summary": json.loads(summary) if summary else None,
            "exercises": json.loads(exercises) if exercises else [],
            "chat_history": chat_data  # 包含所有类型的聊天记录
        }
    
    def get_file_record_cache(self, file_id: str) -> dict:
        redis_key = f"file_upload:{file_id}"
        return self.conn.hgetall(redis_key)
    

    def get_group_discussion(self, session_id: str, lesson_index: int) -> str:
        base_key = f"session:{session_id}:lesson:{lesson_index}"
        script=self.conn.hget(f"{base_key}:data", "script")
        return json.loads(script)['Group Discussion Questions']
        

    def update_teaching_script(self, session_id: str, lesson_script: dict):
        """更新教学进度"""
        lesson_index = self.conn.hget(f"session:{session_id}", "current_lesson")
        base_key = f"session:{session_id}:lesson:{lesson_index}"
        # print(lesson_script)
        
        with self.conn.pipeline() as pipe:
            # 保存课程脚本
            pipe.hset(f"{base_key}:data", "script", json.dumps(lesson_script))
            # 重置TTL
            pipe.expire(f"session:{session_id}", self.ttl)
            pipe.expire(f"{base_key}:data", self.ttl)
            pipe.execute()

    def update_lesson_summary(self, session_id: str, summary: str):
        """更新教学总结"""
        lesson_index = self.conn.hget(f"session:{session_id}", "current_lesson")
        base_key = f"session:{session_id}:lesson:{lesson_index}"

        with self.conn.pipeline() as pipe:
            pipe.hset(f"{base_key}:data", "summary", summary)
            pipe.expire(f"session:{session_id}", self.ttl)
            pipe.expire(f"{base_key}:data", self.ttl)
            pipe.execute()

    def update_lesson_exercises(self, session_id: str, exercises: dict):
        """更新练习题"""
        lesson_index = self.conn.hget(f"session:{session_id}", "current_lesson")
        base_key = f"session:{session_id}:lesson:{lesson_index}"

        with self.conn.pipeline() as pipe:
            pipe.hset(f"{base_key}:data", "exercises", json.dumps(exercises))
            pipe.expire(f"session:{session_id}", self.ttl)
            pipe.expire(f"{base_key}:data", self.ttl)
            pipe.execute()

    def start_new_lesson(self, session_id: str):
        """开始新的课程小节"""
        with self.conn.pipeline() as pipe:
            # 原子操作递增课程索引
            pipe.hincrby(f"session:{session_id}", "current_lesson", 1)
            pipe.execute()
            
        current_lesson = self.conn.hget(f"session:{session_id}", "current_lesson")
        return int(current_lesson)

    def save_chat_history(self, session_id: str, messages: list, step_type: Step):
        """保存聊天记录到指定类型的Redis列表"""
        # 参数校验
        if not isinstance(step_type, Step):
            raise ValueError(f"Invalid step type: {step_type}")
        
        # 获取当前课时索引
        lesson_index = self.conn.hget(f"session:{session_id}", "current_lesson")
        if not lesson_index:
            raise ValueError(f"Session {session_id} has no current_lesson")
        
        # 构造类型专属的Redis键
        type_key = f"session:{session_id}:lesson:{lesson_index}:chat_history:{step_type.value}"
        print(type_key)

        # 序列化消息并存储
        serialized = [json.dumps(msg) for msg in messages]
        print(serialized)
        if serialized:  # 避免空列表操作
            self.conn.rpush(type_key, *serialized)
            self.conn.expire(type_key, self.ttl)  # 设置相同TTL

    def migrate_session_data(self, redis_session_id: str):
        # 获取 Redis 中的会话基础数据
        session_key = f"session:{redis_session_id}"
        session_data = lesson_cache.conn.hgetall(session_key)
        
        # 构建 Cosmos 文档结构
        cosmos_doc = {
            "session_id": redis_session_id,
            "type": "session",
            "user_id": session_data["user_id"],
            "file_id": session_data["file_id"],
            "currentLesson": int(session_data["current_lesson"]),
            "totalLessons": int(session_data["total_lessons"]),
            "lessons": []
        }
        
        # 遍历每个课程数据
        for lesson_idx in range(cosmos_doc["totalLessons"]):
            lesson_data = lesson_cache.get_lesson_state(redis_session_id, lesson_idx)
            
            # 转换聊天记录结构
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
        # 从 Redis 获取原始数据
        redis_key = f"file_upload:{file_id}"
        file_data = lesson_cache.conn.hgetall(redis_key)
        
        # 构建 Cosmos 文档
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


# 测试用例
def test_lesson_flow():
    cache = LessonCache()
    
    # # 模拟用户创建会话
    # user_id = "user_123"
    # material_id = "material_456"
    # session_id = cache.create_session(user_id, material_id, total_lessons=4)
    
    # # 模拟第一节课
    # lesson_script = {
    #     "topic": "Python Basics",
    #     "key_points": ["Variables", "Data Types"],
    #     "discussion_topic": "Why Python is popular?"
    # }
    # cache.update_teaching_script(session_id, lesson_script)
    
    # # 模拟保存聊天记录
    # chat_messages = [
    #     {"role": "teacher", "content": "Let's start with variables"},
    #     {"role": "user", "content": "What's a string?"}
    # ]
    # cache.save_chat_history(session_id, chat_messages, Step.TEACHING)
    
    # 获取当前状态
    state = cache.get_lesson_state("session_94f6b7de-011a-4142-9fd8-2406761a841c", 0)
    print("Lesson State:", state)
    
    # # 切换到下一节课
    # cache.start_new_lesson(session_id)
    # print("Current Lesson:", cache.conn.hget(f"session:{session_id}", "current_lesson"))

if __name__ == "__main__":
    test_lesson_flow()