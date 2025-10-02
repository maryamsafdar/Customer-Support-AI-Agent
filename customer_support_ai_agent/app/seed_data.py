from .db import Base, engine, SessionLocal
from .models import FAQ

Base.metadata.create_all(bind=engine)

faqs = [
    FAQ(
        question="What are your support hours?",
        answer="Our support hours are 9am–5pm (Mon–Fri, local time).",
        keywords="hours,time,support,available,timing"
    ),
    FAQ(
        question="How long do refunds take?",
        answer="Refunds are processed within 3–5 business days after approval.",
        keywords="refunds,returns,money back,process,quickly"
    ),
    FAQ(
        question="Do you ship internationally?",
        answer="Yes, we ship to most countries. Shipping fees apply at checkout.",
        keywords="ship,shipping,international,worldwide,abroad"
    ),
    FAQ(
        question="Where can I track my order?",
        answer="Use the tracking link in your confirmation email or your account page.",
        keywords="track,tracking,order,delivery,status"
    )
]

db = SessionLocal()
db.query(FAQ).delete()
for f in faqs:
    db.add(f)
db.commit()
db.close()

print("✅ Seeded FAQs")
