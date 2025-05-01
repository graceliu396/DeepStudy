import uuid
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from app.tools.azure_cosmos_db import create_file_record
from semantic_kernel.contents import ChatHistory
from fastapi import APIRouter, UploadFile, File
from schemas.uploadFile import *
from tools.azure_document_intelligence import analyze_pdf
from app.core.kernel import kernel, load_prompt
from app.api.deps import CurrentUser
from app.tools.azure_redis_for_cache import lesson_cache


router = APIRouter(tags=["parse"])


@router.post("/material/upload", response_model=FileUpload)
async def parse_file(file: UploadFile = File(...)):

    file_content = await file.read()
    full_text = analyze_pdf(file_content)
    print(f"full_text:> {full_text}")

    req_settings = kernel.get_prompt_execution_settings_from_service_id(service_id="deepseek-chat")
    req_settings.max_tokens = 2000
    req_settings.temperature = 0.7
    req_settings.top_p = 0.8
    req_settings.response_format = Plan   
    req_settings.function_choice_behavior = FunctionChoiceBehavior.Auto(filters={"excluded_plugins": ["chat"]})

    chat_function = kernel.add_function(
        prompt=load_prompt("file_parser") + """{{$chat_history}}""",
        function_name="parse_lesson_plan",
        plugin_name="parse_lesson_plan",
        prompt_execution_settings=req_settings,
    )
    history = ChatHistory()
    history.add_user_message(full_text)

    response = await kernel.invoke(
        chat_function,
        chat_history=history,
    )

    reasoned_result = Plan.model_validate_json(response.value[0].content)
    print(f"Mosscap:> {reasoned_result}")
    lesson_plan_json = reasoned_result.model_dump()
    total_lessons=len(lesson_plan_json['lesson_sequence'])

    file_record = FileUpload(
        id=str(uuid.uuid4()),
        user_id="3",
        subject=reasoned_result.subject,
        file_topic=reasoned_result.topic,
        grade=reasoned_result.grade,
        file_content=full_text,
        lesson_plan=reasoned_result,
        total_lessons=total_lessons
    )

    lesson_cache.create_file_record_cache(file_record.model_dump())
    lesson_cache.migrate_file_data(file_record.id)

    return file_record.model_dump()
