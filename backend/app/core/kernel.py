from semantic_kernel import Kernel
from openai import AsyncOpenAI
from semantic_kernel.connectors.ai.open_ai.services.azure_chat_completion import AzureChatCompletion
from semantic_kernel.connectors.ai.open_ai.services.open_ai_chat_completion import OpenAIChatCompletion

import os
from app.core.config import settings


def load_prompt(agent_name):
    """Loads the prompt for a given agent from a file."""
    file_path = os.path.join(settings.PROMPT_DIR, f"{agent_name}.prompty")
    print(f"Loading prompt for {agent_name} from {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"Prompt file not found for {agent_name}, using default placeholder.")
        return "You are an AI banking assistant."  # Fallback default prompt

deepseek_chat_service = OpenAIChatCompletion(
    service_id="deepseek-chat",
    ai_model_id="deepseek-chat",    # or "deepseek-reasoner"
    async_client=AsyncOpenAI(
        api_key=settings.DEEPSEEK_API_KEY,
        base_url=settings.DEEPSEEK_BASE_URL
    ),
)

azure_openai_service = AzureChatCompletion(
    service_id="azure_openai",
    endpoint=settings.AZURE_OPENAI_ENDPOINT,
    api_key=settings.AZURE_OPENAI_API_KEY,
    deployment_name=settings.AZURE_OPENAI_CHAT_DEPLOYMENT_NAME,
    api_version="2024-12-01-preview"
)


kernel = Kernel()
kernel.add_service(deepseek_chat_service)
kernel.add_service(azure_openai_service)


