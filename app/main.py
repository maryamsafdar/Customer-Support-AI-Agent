import os, re
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from .db import Base, engine, get_db
from .models import FAQ, Ticket
from .schemas import AskRequest, AskResponse, TicketCreate, TicketOut, FAQCreate, FAQOut
from .faq_matcher import best_faq, top_k_faqs
from .ai import answer_with_ai

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Customer Support AI Agent", version="2.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

# ---------- Tunables (override via .env) ----------
FAQ_STRICT_THRESHOLD = float(os.getenv("FAQ_STRICT_THRESHOLD", "0.65"))   # strong → FAQ
AI_TRY_MIN_THRESHOLD = float(os.getenv("AI_TRY_MIN_THRESHOLD", "0.30"))   # weak/medium → try AI
AI_CONF_THRESHOLD    = float(os.getenv("AI_CONFIDENCE_THRESHOLD", "0.60"))# AI must clear this
TOPK_FOR_AI          = int(os.getenv("TOPK_FOR_AI", "3"))
# --------------------------------------------------

def looks_gibberish(q: str) -> bool:
    # no alphabetic tokens of length >= 3
    return len(re.findall(r"[A-Za-z]{3,}", q or "")) == 0

def build_context_from_topk(scored_faqs, max_chars: int = 1800) -> str:
    parts = [f"Q: {faq.question}\nA: {faq.answer}" for faq, _ in scored_faqs]
    return "\n\n".join(parts)[:max_chars]

@app.get("/health")
def health():
    return {"status": "ok"}

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
            source="ticket", ticket_id=t.id
        )

    # 1) Best FAQ then branch on thresholds
    bf = best_faq(q, db)
    if bf:
        faq, faq_score = bf

        # 1a) Strong FAQ → return FAQ
        if faq_score >= FAQ_STRICT_THRESHOLD:
            return AskResponse(
                answer=str(faq.answer),
                source="faq",
                score=round(float(faq_score), 3),
                ticket_id=None,
            )

        # 1b) Weak/medium FAQ → try AI on top-k FAQs as context
        if faq_score >= AI_TRY_MIN_THRESHOLD:
            topk = top_k_faqs(q, db, k=TOPK_FOR_AI)
            context = build_context_from_topk(topk)
            ai_ans, ai_score = answer_with_ai(q, context)
            if ai_ans and ai_score >= AI_CONF_THRESHOLD:
                return AskResponse(
                    answer=ai_ans,
                    source="ai",
                    score=round(float(ai_score), 3),
                    ticket_id=None,
                )

    # 2) No useful FAQ signal or AI not confident → ticket
    t = Ticket(question=q)
    db.add(t); db.commit(); db.refresh(t)
    return AskResponse(
        answer="I couldn't confidently answer that. A support ticket has been created.",
        source="ticket",
        ticket_id=t.id,
    )

# ----- Tickets & FAQs (unchanged) -----
@app.post("/tickets", response_model=TicketOut)
def create_ticket(payload: TicketCreate, db: Session = Depends(get_db)):
    t = Ticket(question=payload.question, email=payload.email, name=payload.name)
    db.add(t); db.commit(); db.refresh(t)
    return t

@app.get("/tickets", response_model=list[TicketOut])
def list_tickets(db: Session = Depends(get_db)):
    tickets = db.query(Ticket).order_by(Ticket.created_at.desc()).all()
    return jsonable_encoder(tickets)

@app.get("/tickets/{ticket_id}", response_model=TicketOut)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    t = db.get(Ticket, ticket_id)
    if not t: raise HTTPException(status_code=404, detail="Ticket not found")
    return t

@app.post("/faqs", response_model=FAQOut)
def create_faq(payload: FAQCreate, db: Session = Depends(get_db)):
    f = FAQ(question=payload.question, answer=payload.answer, keywords=payload.keywords or "")
    db.add(f); db.commit(); db.refresh(f)
    return f

@app.get("/faqs", response_model=list[FAQOut])
def list_faqs(db: Session = Depends(get_db)):
    return db.query(FAQ).all()
