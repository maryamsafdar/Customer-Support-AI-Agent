from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from . import db, models, schemas

app = FastAPI(title="Customer Support AI Agent")

# Create tables on startup
models.Base.metadata.create_all(bind=db.engine)

def get_db():
    database = db.SessionLocal()
    try:
        yield database
    finally:
        database.close()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/faqs", response_model=list[schemas.FAQOut])
def list_faqs(db: Session = Depends(get_db)):
    return db.query(models.FAQ).all()

@app.get("/tickets", response_model=list[schemas.TicketOut])
def list_tickets(db: Session = Depends(get_db)):
    return db.query(models.Ticket).all()

@app.post("/tickets", response_model=schemas.TicketOut)
def create_ticket(ticket: schemas.TicketCreate, db: Session = Depends(get_db)):
    new_ticket = models.Ticket(
        question=ticket.question,
        name=ticket.name,
        email=ticket.email
    )
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    return new_ticket
