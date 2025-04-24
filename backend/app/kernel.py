from semantic_kernel import Kernel
from openai import AsyncOpenAI
from semantic_kernel.connectors.ai.open_ai.services.azure_chat_completion import AzureChatCompletion
from semantic_kernel.connectors.ai.open_ai.services.open_ai_chat_completion import OpenAIChatCompletion
from semantic_kernel.agents import AgentGroupChat, ChatCompletionAgent

import os
from config import __PROMPT_DIR__


def load_prompt(agent_name):
    """Loads the prompt for a given agent from a file."""
    file_path = os.path.join(__PROMPT_DIR__, f"{agent_name}.prompty")
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
        api_key="sk-XImXi6sCanG1yu9oznm9TwwPj0mAhxSb0jVYWN0aM9m2UnfJ",
        base_url="https://fast.xeduapi.com",
    ),
)
kernel = Kernel()
kernel.add_service(deepseek_chat_service)


