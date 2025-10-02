
# Customer Support AI Agent (FastAPI + SQLite + Transformers + Streamlit)

**Goal:** A lightweight customer support agent that:
- Answers FAQs from a small SQLite knowledge base
- Falls back to a free Hugging Face Q&A model when unsure
- Creates a support ticket if confidence is low
- Exposes clean REST API endpoints for integration
- Optional Streamlit chat UI

---

## 🧰 Tech Stack (Free & Beginner‑Friendly)
- **Backend:** Python, FastAPI
- **DB:** SQLite (file-based, no setup)
- **AI:** Hugging Face `transformers` pipeline (`distilbert-base-uncased-distilled-squad`)
- **Frontend (optional):** Streamlit chat UI (or basic HTML/JS)

## 📁 Project Structure
```text
customer-support-ai/
├─ app/
│  ├─ main.py              # FastAPI app + endpoints
│  ├─ db.py                # SQLAlchemy engine/session
│  ├─ models.py            # ORM models (FAQ, Ticket)
│  ├─ schemas.py           # Pydantic request/response models
│  ├─ faq_matcher.py       # Rule-based FAQ keyword matcher
│  ├─ ai.py                # Hugging Face QA model wrapper
│  └─ seed_data.py         # Seed initial FAQs
├─ data/
│  └─ support.db           # SQLite DB (autocreated)
├─ frontend/
│  ├─ streamlit_app.py     # Optional: chat-style UI
│  ├─ index.html           # Optional: barebones HTML demo
│  ├─ script.js            # Optional: fetch() -> /ask
│  └─ assets/
│     └─ styles.css        # Optional: minimal extra styling
├─ requirements.txt
├─ .env.example
└─ README.md
```

---
## 🗓️ 5‑Day Build Plan (Beginner → Intermediate)

**Day 1 – Project Setup**
1. Create a virtual environment and install dependencies.
2. Scaffold folders and files (see structure above).
3. Initialize FastAPI and SQLite.

**Day 2 – FAQ System & Tickets**
1. Implement SQLAlchemy models for `FAQ` and `Ticket`.
2. Implement rule‑based FAQ matcher (keyword overlap).
3. Add CRUD endpoints to list/add FAQs and create/view tickets.

**Day 3 – AI Answering**
1. Add Hugging Face QA pipeline (`distilbert-base-uncased-distilled-squad`).
2. Build context from FAQs; attempt AI answer when no FAQ match.
3. If AI confidence < threshold ⇒ create ticket automatically.

**Day 4 – REST API**
- `/health`, `/ask`, `/tickets` (POST/GET), `/tickets/{id}`, `/faqs` (GET/POST)
- Enable CORS for simple HTML/JS frontends.

**Day 5 – Optional Streamlit Frontend + Deploy**
1. Streamlit chat UI using `st.chat_message` (professional, clean).
2. Sidebar showing Open Tickets + manual ticket form.
3. Deploy options (free):
   - **Streamlit Cloud**: Deploy `frontend/streamlit_app.py` (standalone app).
   - **Hugging Face Spaces**: Deploy FastAPI backend (as `main:app`) **and/or** the Streamlit app.

---
## ▶️ Quick Start (Local)
```bash
# 0) (optional) python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 1) Seed example FAQs (creates ./data/support.db)
python -m app.seed_data

# 2) Run FastAPI backend
uvicorn app.main:app --reload --port 8000

# 3) (Option A) Minimal HTML demo
#     Open frontend/index.html in your browser (will call http://localhost:8000/ask)
#
# 3) (Option B) Streamlit chat UI (set BASE_URL in sidebar to your API URL)
streamlit run frontend/streamlit_app.py
```

**Environment variables (optional)**: copy `.env.example` → `.env` and tune:
```
MODEL_NAME=distilbert-base-uncased-distilled-squad
AI_CONFIDENCE_THRESHOLD=0.45
```

---
## 🔌 REST API Endpoints

- `GET /health` → `{ "status": "ok" }`
- `POST /ask`  
  **Body:** `{ "question": "string" }`  
  **Response:** `{ "answer": "…", "source": "faq|ai|ticket", "score": number|null, "ticket_id": int|null }`

- `POST /tickets`  
  **Body:** `{ "question": "string", "email": "optional", "name": "optional" }`

- `GET /tickets` → list tickets (most recent first)
- `GET /tickets/{id}` → single ticket
- `GET /faqs` → list FAQs
- `POST /faqs`  
  **Body:** `{ "question": "…", "answer": "…", "keywords": "comma,separated,words" }`

---
## 🧪 How the Answering Works

1) **FAQ match first** using simple keyword overlap (fast + deterministic).  
2) **AI model second**: builds a context from all FAQs, tries Q&A pipeline.  
3) **Ticket fallback** when AI confidence < `AI_CONFIDENCE_THRESHOLD`.

> Tip: Improve FAQ coverage & keywords to reduce tickets and AI load.

---
## 🎨 Professional Streamlit UI

- Clean, chat‑style layout with avatars and subtle separators
- Persistent session history
- Sidebar: API Base URL, Open Tickets, Manual Ticket creation
- Handles loading states and error messages gracefully

---
## ☁️ Deploy (Free)

### Option 1: Streamlit Cloud
1. Push this folder to GitHub.
2. On Streamlit Cloud, create a new app → point to `frontend/streamlit_app.py`.
3. In the sidebar of the deployed app, set **API Base URL** to your FastAPI endpoint.

### Option 2: Hugging Face Spaces
- **Backend Space (FastAPI)**:
  - Create a Space → choose *Docker* or *SDK* → `fastapi` template.
  - Set `app.main:app` as the entry point (or use provided HF template).
- **Frontend Space (Streamlit)**:
  - Create a Space → `streamlit` template → set `frontend/streamlit_app.py`.
  - Point the sidebar **API Base URL** to your backend Space URL.

---
## ⚙️ Notes

- First run will download the QA model (~260MB). Subsequent runs are cached.
- Everything runs on CPU; no GPU required.
- You can later swap SQLite → Postgres and replace the model with a better one.
