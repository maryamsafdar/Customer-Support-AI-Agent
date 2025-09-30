from pydantic import BaseModel
from datetime import datetime

class FAQOut(BaseModel):
    id: int
    question: str
    answer: str
    keywords: str | None = None

    class Config:
        from_attributes = True   # replaces old orm_mode=True

class TicketCreate(BaseModel):
    question: str
    name: str | None = None
    email: str | None = None

class TicketOut(BaseModel):
    id: int
    question: str
    name: str | None
    email: str | None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
