import re
from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from rapidfuzz import fuzz
from .models import FAQ

_word_re = re.compile(r"\b\w+\b", re.UNICODE)
_STOP = {"the","a","an","is","are","do","does","you","your","yours","to","for","and","or","of","at","in","on","by","with"}

def _normalize(text: str) -> list[str]:
    return [w.lower() for w in _word_re.findall(text or "") if w.lower() not in _STOP]

def _token_set(text: str) -> set[str]:
    return set(_normalize(text))

def _keyword_set(keywords: str | None) -> set[str]:
    if not keywords:
        return set()
    parts = [p.strip().lower() for p in keywords.split(",") if p.strip()]
    # allow multi-word keywords to act as tokens too
    out = set()
    for p in parts:
        out.add(p)
        out |= _token_set(p)
    return out

def _score_pair(q: str, faq: FAQ) -> float:
    """Blended score in [0,1]: 65% fuzzy, 35% token overlap (keywords > question)."""
    q = (q or "").strip().lower()
    q_tokens = _token_set(q)
    key_set = _token_set(str(faq.keywords or "")) or _token_set(str(faq.question))

    # Jaccard overlap
    denom = len(q_tokens | key_set)
    jacc  = (len(q_tokens & key_set) / denom) if denom else 0.0

    # Fuzzy against question and (question+answer)
    f1 = fuzz.token_set_ratio(q, str(faq.question)) / 100.0
    f2 = fuzz.token_set_ratio(q, f"{faq.question} {faq.answer}") / 100.0
    fuzzy = max(f1, f2)

    return 0.65 * fuzzy + 0.35 * jacc

def best_faq(question: str, db: Session) -> Optional[Tuple[FAQ, float]]:
    q = (question or "").strip().lower()
    if not q:
        return None
    best: Optional[FAQ] = None
    best_score = 0.0
    for faq in db.query(FAQ).all():
        s = _score_pair(q, faq)
        if s > best_score:
            best_score, best = s, faq
    return (best, best_score) if best else None

def top_k_faqs(question: str, db: Session, k: int = 3) -> List[Tuple[FAQ, float]]:
    q = (question or "").strip().lower()
    scored: List[Tuple[FAQ, float]] = []
    for faq in db.query(FAQ).all():
        scored.append((faq, _score_pair(q, faq)))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:max(1, k)]
