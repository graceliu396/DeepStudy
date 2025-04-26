from app.utils.faiss_helper import load_faiss
from app.config import embedder, llm
from app.models.schema import Weakness, Question
import json
from typing import List

def retrieve_questions(topic: str, weaknesses: List[Weakness]) -> List[Question]:
    db = load_faiss()
    retriever = db.as_retriever(search_type="similarity", k=3)
    results = []
    for weak in weaknesses:
        query = f"Lesson topic: {topic}. Weakness: {weak.Description}"
        docs = retriever.get_relevant_documents(query)
        context = "\n".join([d.page_content for d in docs])
        prompt = f"""
Based on context and weakness, generate 1 MCQ JSON:
{{"Question":"...","Options":{{...}},"Answer":"...","Explanation":"..."}}
Context:
{context}
Weakness: {weak.Description}
"""
        response = llm.invoke(prompt)
        results.append(Question(**json.loads(response)))
    return results
