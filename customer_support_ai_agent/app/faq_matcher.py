import re
from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from .models import FAQ
from rapidfuzz import fuzz

_word_re = re.compile(r"\b\w+\b", re.UNICODE)

def _normalize(text: str) -> list[str]:
    return [w.lower() for w in _word_re.findall(text or "")]

def _token_set(text: str) -> set[str]:
    return set(_normalize(text))

def _faq_keyset(faq: FAQ) -> set[str]:
    """
    Prefer keywords for matching; fall back to tokenized FAQ question.
    """
    ks = _token_set(faq.keywords or "")
    return ks or _token_set(faq.question)

def _score_pair(q: str, faq: FAQ) -> float:
    """
    Blended score in [0,1]:
      - 60% rapidfuzz token_set_ratio (handles word order / partials)
      - 40% Jaccard overlap on (question tokens vs FAQ keywords/tokens)
    """
    q_tokens = _token_set(q)
    key_set  = _faq_keyset(faq)

    # Jaccard overlap
    denom = len(q_tokens | key_set)
    jacc  = (len(q_tokens & key_set) / denom) if denom else 0.0

    # RapidFuzz normalized
    fuzzy = fuzz.token_set_ratio(q, faq.question) / 100.0

    return 0.60 * fuzzy + 0.40 * jacc

def best_faq(question: str, db: Session) -> Optional[Tuple[FAQ, float]]:
    """
    Return the single best matching FAQ and its blended score (0..1),
    WITHOUT applying any threshold. Callers decide thresholds.
    """
    q = (question or "").strip().lower()
    if not q:
        return None

    faqs: List[FAQ] = db.query(FAQ).all()
    best: Optional[FAQ] = None
    best_score = 0.0
    for faq in faqs:
        s = _score_pair(q, faq)
        if s > best_score:
            best_score = s
            best = faq

    if best is None:
        return None
    return best, best_score

def top_k_faqs(question: str, db: Session, k: int = 3) -> List[Tuple[FAQ, float]]:
    """
    Return top-k FAQs with their scores (no threshold), sorted desc.
    Use this to build a compact AI context.
    """
    q = (question or "").strip().lower()
    faqs: List[FAQ] = db.query(FAQ).all()
    scored: List[Tuple[FAQ, float]] = []
    for faq in faqs:
        scored.append((faq, _score_pair(q, faq)))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:max(1, k)]

def match_faq(question: str, db: Session, min_score: float = 0.35) -> Optional[Tuple[FAQ, float]]:
    """
    Try to match a FAQ by combining token overlap (Jaccard) and fuzzy matching.
    Returns the best FAQ and score if above min_score, else None.
    """
    q = (question or "").strip().lower()
    q_tokens = _token_set(q)

    best = None
    best_score = 0.0

    faqs: List[FAQ] = db.query(FAQ).all()
    for faq in faqs:
        # Use keywords if available, else fall back to FAQ text
        key_set = _token_set(faq.keywords or "") or _token_set(faq.question)

        # Jaccard overlap
        jaccard = len(q_tokens & key_set) / len(q_tokens | key_set) if (q_tokens | key_set) else 0.0
        # Fuzzy ratio
        fuzzy = fuzz.token_set_ratio(q, faq.question) / 100.0

        # Weighted score
        score = (0.6 * fuzzy) + (0.4 * jaccard)

        if score > best_score:
            best_score = score
            best = faq

    if best and best_score >= min_score:
        return best, best_score
    return None