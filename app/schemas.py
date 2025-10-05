from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str
    source: str
    score: Optional[float] = None
    ticket_id: Optional[int] = None

class FAQCreate(BaseModel):
    question: str
    answer: str
    keywords: Optional[str] = None

class FAQOut(BaseModel):
    id: int
    question: str
    answer: str
    keywords: Optional[str]

    class Config:
        orm_mode = True

class TicketCreate(BaseModel):
    question: str
    email: Optional[str] = None
    name: Optional[str] = None

class TicketOut(BaseModel):
    id: int 
    question: str
    name: str | None = None
    email: str | None = None
    status: str | None = "open"
    created_at: datetime   # <- let Pydantic handle datetime

    class Config:
        from_attributes = True   # replaces old orm_mode=True

