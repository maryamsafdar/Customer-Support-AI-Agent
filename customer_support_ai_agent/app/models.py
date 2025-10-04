from sqlalchemy import Column, Integer, String, Text, DateTime, func
from .db import Base

class FAQ(Base):
    __tablename__ = "faqs"
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    keywords = Column(Text, nullable=True)

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)  
    question = Column(String, nullable=False)
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    status = Column(String, default="open")   
    created_at = Column(DateTime, server_default=func.now())
