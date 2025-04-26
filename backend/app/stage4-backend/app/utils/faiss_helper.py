from langchain.vectorstores import FAISS
from app.config import embedder

def load_faiss():
    return FAISS.load_local("seed_faiss_index", embedder)
