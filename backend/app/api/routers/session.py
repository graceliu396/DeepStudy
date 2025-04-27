import uuid
import json
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from app.tools.azure_cosmos_db import create_file_record
from semantic_kernel.contents import ChatHistory
from fastapi import APIRouter, UploadFile, File
from schemas.uploadFile import *
from tools.azure_document_intelligence import analyze_pdf
from app.core.kernel import kernel, load_prompt
from app.api.deps import CurrentUser
from app.tools.azure_cosmos_db import fetch_file_by_id
from app.tools.azure_redis_for_cache import lesson_cache
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from app.agent.stage0_preparing import generate_teaching_script

from app.schemas.chatHistory import Step


router = APIRouter(tags=["study"])

# 用户点击“开始学习”，进入备课环节
@router.post("/session/start")
async def start_session(file_id: str):
    file_record=lesson_cache.get_file_record_cache(file_id)
    #print(type(file_record['lesson_plan']))
    #print(type(eval(file_record['lesson_plan'])))
    session_id=lesson_cache.create_session(file_record['user_id'], file_id, file_record['total_lessons'])
    #print(type((eval(file_record['lesson_plan']))['lesson_sequence']))
    mini_lesson_plan=(eval(file_record['lesson_plan']))['lesson_sequence'][0]
    teaching_script= await generate_teaching_script(str(mini_lesson_plan))
    # print(type(teaching_script))
    print(teaching_script)
    lesson_cache.update_teaching_script(session_id, teaching_script)

    return {"message": "Lesson preparation completed!", "session_id": session_id, "lesson_index": 0}


# 用户上完一节课点击“下一节课”，进入下一节课的备课环节
@router.post("/session/{session_id}/next_lesson")
async def next_lesson(session_id: str, file_id: str):
    lesson_cache.start_new_lesson(session_id)
    lesson_index=lesson_cache.conn.hget(f"session:{session_id}", "current_lesson")
    file_record=lesson_cache.get_file_record_cache(file_id)
    mini_lesson_plan=file_record['lesson_plan']['lesson_sequence'][lesson_index]
    teaching_script= await generate_teaching_script(str(mini_lesson_plan))
    lesson_cache.update_teaching_script(session_id, teaching_script)

    return {"message": "Lesson preparation completed!", "session_id": session_id, "lesson_index": lesson_index}


# 备课结束，点击“开始上课
@router.post("/session/{session_id}/lesson/{lesson_index}/teaching")
async def start_mini_lesson(session_id: str, lesson_index: int):
    script=lesson_cache.get_lesson_state(session_id, lesson_index)['script']
    # TODO: 实时接收用户的输入，生成Teacher的输出
    # Confused：不知道前端是怎么实现的，要怎么接起来（Chainlit？WebSocket？）
    return





# 开始小组讨论
@router.post("/session/{session_id}/lesson/{lesson_index}/discussion")
async def start_discussion(session_id: str, lesson_index: int):
    group_discussion_question=lesson_cache.get_group_discussion(session_id, lesson_index)
    # TODO: 小组讨论
    # lesson_cache.save_chat_history(session_id, message_list, Step.GROUP_DISCUSSION)
    return





# 开始进行总结和练习
@router.post("/session/{session_id}/lesson/{lesson_index}/summary")
async def start_summary(session_id: str, lesson_index: int):
    # TODO: 总结和练习
    # lesson_cache.update_lesson_exercises(session_id, exercises)
    # lesson_cache.update_lesson_summary(session_id, summary)
    # lesson_cache.save_chat_history(session_id, message_list, Step.FINAL_SUMMARY)
    # lesson_cache.save_chat_history(session_id, message_list, Step.PRACTICE)
    return


# 用户点击退出 OR 全部课程上完退出
@router.post("/session/{session_id}/exit")
async def exit_session(session_id: str):
    # TODO: 退出学习
    # TODO: reids缓存全部更新到数据库中，删除缓存
    lesson_cache.migrate_session_data(session_id)
