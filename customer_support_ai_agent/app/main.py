
import os
import re
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .db import Base, engine, get_db
from .models import FAQ, Ticket
from .schemas import AskRequest, AskResponse, TicketCreate, TicketOut, FAQCreate, FAQOut
from .faq_matcher import best_faq, top_k_faqs,match_faq
from .ai import answer_with_ai
from fastapi.encoders import jsonable_encoder

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Customer Support AI Agent", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

AI_THRESHOLD = float(os.getenv("AI_CONFIDENCE_THRESHOLD", "0.5"))


@app.get("/health")
def health():
    return {"status": "ok"}

# Tunables (env overrides allowed)
FAQ_STRICT_THRESHOLD = float(os.getenv("FAQ_STRICT_THRESHOLD", "0.65"))  # was 0.72; lower a bit to recover FAQ hits
AI_TRY_MIN_THRESHOLD = float(os.getenv("AI_TRY_MIN_THRESHOLD", "0.25"))
AI_CONF_THRESHOLD    = float(os.getenv("AI_CONFIDENCE_THRESHOLD", "0.50"))


def looks_gibberish(q: str) -> bool:
    return len(re.findall(r"[A-Za-z]{3,}", q or "")) == 0

def _build_context_from_topk(scored_faqs, max_chars: int = 1800) -> str:
    """
    Compact context: multiple Q/A pairs. Keeps the model grounded in your KB.
    """
    parts = [f"Q: {faq.question}\nA: {faq.answer}" for faq, _ in scored_faqs]
    ctx = "\n\n".join(parts)
    return ctx[:max_chars]

@app.post("/ask", response_model=AskResponse)
def ask(payload: AskRequest, db: Session = Depends(get_db)):
    q = (payload.question or "").strip()
    if not q:
        raise HTTPException(status_code=400, detail="Question required.")

    # 0) Obvious gibberish → ticket
    if looks_gibberish(q):
        t = Ticket(question=q)
        db.add(t); db.commit(); db.refresh(t)
        return AskResponse(
            answer="I couldn't confidently answer that. A support ticket has been created.",
            source="ticket",
            ticket_id=t.id
        )

    # 1) Best FAQ (no early return until we check thresholds)
    bf = best_faq(q, db)  # returns (faq, score) or None
    if bf:
        faq, faq_score = bf

        # 1a) Strong FAQ match → FAQ
        if faq_score >= FAQ_STRICT_THRESHOLD:
            return AskResponse(
                answer=faq.answer,
                source="faq",
                score=round(float(faq_score), 3),
                ticket_id=None
            )

        # 1b) Weak/medium match → try AI on top-k FAQ context
        if faq_score >= AI_TRY_MIN_THRESHOLD:
            topk = top_k_faqs(q, db, k=3)
            context = _build_context_from_topk(topk)
            try:
                a, a_score = answer_with_ai(q, context)
            except Exception:
                a, a_score = "", 0.0

            if a and a_score >= AI_CONF_THRESHOLD:
                return AskResponse(
                    answer=a,
                    source="ai",
                    score=round(float(a_score), 3),
                    ticket_id=None
                )
            # fall-through to ticket if AI not confident

    # 2) No useful FAQ or AI not confident → ticket
    t = Ticket(question=q)
    db.add(t); db.commit(); db.refresh(t)
    return AskResponse(
        answer="I couldn't confidently answer that. A support ticket has been created.",
        source="ticket",
        ticket_id=t.id
    )

    q = (payload.question or "").strip()
    if not q:
        raise HTTPException(status_code=400, detail="Question required.")

    # 0) Obvious gibberish → ticket
    if looks_gibberish(q):
        t = Ticket(question=q)
        db.add(t); db.commit(); db.refresh(t)
        return AskResponse(
            answer="I couldn't confidently answer that. A support ticket has been created.",
            source="ticket",
            ticket_id=t.id
        )

    # 1) Best FAQ match
    bf = best_faq(q, db)
    if bf:
        faq, faq_score = bf

        # Strong FAQ match → FAQ
        if faq_score >= FAQ_STRICT_THRESHOLD:
            return AskResponse(
                answer=faq.answer,
                source="faq",
                score=round(float(faq_score), 3)
            )

        # Weak/medium FAQ match → try AI
        if faq_score >= AI_TRY_MIN_THRESHOLD:
            topk = top_k_faqs(q, db, k=3)
            context = _build_context_from_topk(topk)
            try:
                a, a_score = answer_with_ai(q, context)
            except Exception:
                a, a_score = "", 0.0

            if a and a_score >= AI_CONF_THRESHOLD:
                return AskResponse(
                    answer=a,
                    source="ai",
                    score=round(float(a_score), 3)
                )

    # 2) No strong FAQ and AI not confident → ticket
    t = Ticket(question=q)
    db.add(t); db.commit(); db.refresh(t)
    return AskResponse(
        answer="I couldn't confidently answer that. A support ticket has been created.",
        source="ticket",
        ticket_id=t.id
    )

    q = (payload.question or "").strip()
    if not q:
        raise HTTPException(status_code=400, detail="Question required.")
    # 0) Obvious gibberish → ticket
    if looks_gibberish(q):
        t = Ticket(question=q)
        db.add(t); db.commit(); db.refresh(t)
        return AskResponse(
            answer="I couldn't confidently answer that. A support ticket has been created.",
            source="ticket",
            ticket_id=t.id
        )

    # 1) FAQ fuzzy match (lower threshold for better recall)
    match = match_faq(q, db, min_score=0.35)
    if match:
        faq, score = match
        return AskResponse(answer=faq.answer, source="faq", score=round(score, 3))

    # 2) AI fallback
    context = "\n".join([f"Q: {f.question}\nA: {f.answer}" for f in db.query(FAQ).all()])
    if context:
        try:
            a, score = answer_with_ai(q, context)
        except Exception:
            a, score = "", 0.0

        if a and score >= AI_THRESHOLD:
            return AskResponse(answer=a, source="ai", score=round(score, 3))

    # 3) Ticket fallback
    t = Ticket(question=q)
    db.add(t)
    db.commit()
    db.refresh(t)
    return AskResponse(
        answer="I couldn't confidently answer that. A support ticket has been created.",
        source="ticket",
        ticket_id=t.id,
    )

    q = (payload.question or "").strip()
    if not q:
        raise HTTPException(status_code=400, detail="Question required.")

    # 0) Obvious gibberish → ticket
    if looks_gibberish(q):
        t = Ticket(question=q)
        db.add(t); db.commit(); db.refresh(t)
        return AskResponse(
            answer="I couldn't confidently answer that. A support ticket has been created.",
            source="ticket",
            ticket_id=t.id
        )

    # 1) Best FAQ (no threshold yet)
    bf = best_faq(q, db)
    if bf:
        faq, faq_score = bf
        # 1a) Strong match → FAQ
        if faq_score >= FAQ_STRICT_THRESHOLD:
            return AskResponse(
                answer=faq.answer,
                source="faq",
                score=round(float(faq_score), 3)
            )
        # 1b) Weak/medium match → try AI over top-k context
        if faq_score >= AI_TRY_MIN_THRESHOLD:
            topk = top_k_faqs(q, db, k=3)
            context = _build_context_from_topk(topk)
            a, a_score = answer_with_ai(q, context)
            if a and a_score >= AI_CONF_THRESHOLD:
                return AskResponse(
                    answer=a,
                    source="ai",
                    score=round(float(a_score), 3)
                )
            # If AI is not confident, we still fall through to ticket below.

    # 2) No useful FAQ signal or AI not confident → ticket
    t = Ticket(question=q)
    db.add(t); db.commit(); db.refresh(t)
    return AskResponse(
        answer="I couldn't confidently answer that. A support ticket has been created.",
        source="ticket",
        ticket_id=t.id
    )
    

@app.post("/tickets", response_model=TicketOut)
def create_ticket(payload: TicketCreate, db: Session = Depends(get_db)):
    t = Ticket(question=payload.question, email=payload.email, name=payload.name)
    db.add(t)
    db.commit()
    db.refresh(t)
    return t



@app.get("/tickets", response_model=list[TicketOut])
def list_tickets(db: Session = Depends(get_db)):
    tickets = db.query(Ticket).all()
    return jsonable_encoder(tickets) 

@app.get("/tickets/{ticket_id}", response_model=TicketOut)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    t = db.get(Ticket, ticket_id)
    if not t:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return t

@app.post("/faqs", response_model=FAQOut)
def create_faq(payload: FAQCreate, db: Session = Depends(get_db)):
    f = FAQ(question=payload.question, answer=payload.answer, keywords=payload.keywords or "")
    db.add(f)
    db.commit()
    db.refresh(f)
    return f

@app.get("/faqs", response_model=list[FAQOut])
def list_faqs(db: Session = Depends(get_db)):
    return db.query(FAQ).all()
