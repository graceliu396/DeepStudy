
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior

from semantic_kernel.contents import ChatHistory
from fastapi import APIRouter, UploadFile, File
from models.lesson_plan import Plan
from tools.azure_document_intelligence import analyze_pdf
from kernel import kernel, load_prompt


router = APIRouter()


@router.post("/upload", response_model=Plan)
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
    return reasoned_result