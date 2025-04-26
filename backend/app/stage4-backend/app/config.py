import os
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
EMBED_MODEL = "text-embedding-ada-002"
LLM_MODEL = "gpt-4"

embedder = OpenAIEmbeddings(openai_api_key=API_KEY)
llm = ChatOpenAI(model_name=LLM_MODEL, temperature=0.3)
