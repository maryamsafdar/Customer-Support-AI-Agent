import os
from transformers import pipeline, Pipeline
from functools import lru_cache

MODEL_NAME = os.getenv("MODEL_NAME", "distilbert-base-uncased-distilled-squad")

@lru_cache(maxsize=1)
def get_qa_model() -> Pipeline:
    # Lazy load + cache
    return pipeline("question-answering", model=MODEL_NAME)

def answer_with_ai(question: str, context: str) -> tuple[str, float]:
    if not context.strip():
        return "", 0.0
    try:
        nlp = get_qa_model()
        result = nlp(question=question, context=context)
        answer = (result.get("answer") or "").strip()
        score = float(result.get("score") or 0.0)
        return answer, score
    except Exception:
        # Fail closed → let caller fall back to ticket
        return "", 0.0
