import csv, os
from sqlalchemy.orm import Session
from .db import Base, engine, SessionLocal
from .models import FAQ

def seed_from_csv(path: str):
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    db: Session = SessionLocal()
    try:
        if db.query(FAQ).count() == 0:
            for r in rows:
                db.add(FAQ(
                    question=r.get('question','').strip(),
                    answer=r.get('answer','').strip(),
                    keywords=r.get('keywords','').strip(),
                ))
            db.commit()
            print(f"Seeded {len(rows)} FAQs.")
        else:
            print("FAQs already exist. Skipping seed.")
    finally:
        db.close()

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'faqs.csv')
    seed_from_csv(csv_path)
