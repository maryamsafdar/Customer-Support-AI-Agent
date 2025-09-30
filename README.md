# 🚀 Customer Support AI Agent – Day 1

This project is a **lightweight AI-powered customer support agent** built with **FastAPI** and **SQLite**.  
On **Day 1**, we set up the **backend foundation**:

- 📂 Project structure  
- ⚙️ Installed dependencies  
- 🗄️ Initialized SQLite database  
- 🧩 Created FAQ + Ticket models  
- 🌱 Seeded sample FAQs  
- 🌐 Exposed initial API endpoints  

---

## 📂 Project Structure
```
customer_support_ai_agent/
│── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI entrypoint
│   ├── db.py            # DB connection setup
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic schemas
│   ├── crud.py          # (future use) DB helper functions
│   └── seed_data.py     # Insert sample FAQs
│
├── data/                # SQLite DB file will be stored here
│
├── requirements.txt     # Python dependencies
└── README.md            # Documentation
```

---

## ⚙️ Requirements

- Python **3.10+**  
- pip (latest version)  

Install dependencies:

```bash
pip install -r requirements.txt
```

### requirements.txt (Day 1 only)
```txt
fastapi
uvicorn
sqlalchemy
pydantic
```

---

## ▶️ Running the API

Start the FastAPI server:

```bash
uvicorn app.main:app --reload --port 8000
```

Expected log:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

---

## 🌱 Seeding the Database

Before testing, run the seed script to load initial FAQs:

```bash
python -m app.seed_data
```

This will populate 4 example FAQs:
- Do you ship internationally?  
- How long do refunds take?  
- What are your support hours?  
- Where can I track my order?  

SQLite database file will be created at:  
`data/support.db`

---

## 🌐 Endpoints (Day 1)

### 1. Health Check
**GET** `/health`

Response:
```json
{"status": "ok"}
```

---

### 2. List FAQs
**GET** `/faqs`

Response:
```json
[
  {
    "id": 1,
    "question": "Do you ship internationally?",
    "answer": "Yes, we ship worldwide.",
    "keywords": "ship,international,worldwide"
  }
]
```

---

### 3. Create Ticket
**POST** `/tickets`

Request body:
```json
{
  "question": "My package is lost",
  "name": "Alice",
  "email": "alice@example.com"
}
```

Response:
```json
{
  "id": 1,
  "question": "My package is lost",
  "name": "Alice",
  "email": "alice@example.com",
  "status": "open",
  "created_at": "2025-09-30T12:10:05"
}
```

---

### 4. List Tickets
**GET** `/tickets`

Response:
```json
[
  {
    "id": 1,
    "question": "My package is lost",
    "name": "Alice",
    "email": "alice@example.com",
    "status": "open",
    "created_at": "2025-09-30T12:10:05"
  }
]
```

---

## 🔍 Testing the API

### Using Swagger UI
Open:
```
http://127.0.0.1:8000/docs
```
You can interact with all endpoints directly from your browser.

---