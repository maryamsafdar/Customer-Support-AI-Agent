from .db import Base, engine, SessionLocal
from .models import FAQ

# Create tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

faqs = [
    FAQ(question="Do you ship internationally?", answer="Yes, we ship worldwide.", keywords="ship,international,worldwide"),
    FAQ(question="How long do refunds take?", answer="Refunds are processed within 3–5 business days.", keywords="refund,return,money back"),
    FAQ(question="What are your support hours?", answer="Our support is available 9am–5pm (Mon–Fri).", keywords="hours,support,time"),
    FAQ(question="Where can I track my order?", answer="You can track orders via your account dashboard.", keywords="track,order,shipping")
]

for f in faqs:
    exists = db.query(FAQ).filter_by(question=f.question).first()
    if not exists:
        db.add(f)

db.commit()
db.close()
print("✅ Seed data inserted")
