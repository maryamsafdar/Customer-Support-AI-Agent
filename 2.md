# 💬 Customer Support AI Agent (FastAPI + SQLite + Transformers + Streamlit)

A lightweight AI-powered support assistant that:
- Answers FAQs from a SQLite knowledge base.
- Uses a Hugging Face Q&A model when unsure.
- Creates support tickets automatically if confidence is low.
- Exposes a clean REST API for integration.
- Includes a Streamlit chat UI frontend.

---

## 🧰 Tech Stack
- **Backend:** FastAPI (Python)
- **Database:** SQLite (auto-created, local)
- **AI Model:** `distilbert-base-uncased-distilled-squad` via Hugging Face Transformers
- **Frontend:** Streamlit (chat-style UI)
- **Deployment:** Railway (backend) + Streamlit Cloud (frontend)

---

## 📁 Project Structure

```text
customer-support-ai-agent/
├─ app/
│  ├─ main.py              # FastAPI app + endpoints
│  ├─ db.py                # SQLAlchemy engine/session
│  ├─ models.py            # ORM models (FAQ, Ticket)
│  ├─ schemas.py           # Pydantic request/response models
│  ├─ faq_matcher.py       # FAQ keyword/fuzzy matcher
│  ├─ ai.py                # Hugging Face Q&A model logic
│  └─ seed_data.py         # Seeds initial FAQs
├─ data/
│  └─ support.db           # SQLite DB (auto-generated)
├─ frontend/
│  ├─ streamlit_app.py     # Streamlit chat UI
│  ├─ index.html           # Optional HTML interface
│  ├─ script.js            # Optional JS demo
│  └─ assets/
│     └─ styles.css
├─ requirements.txt
├─ runtime.txt
├─ Procfile
└─ README.md
```

---

## ▶️ Quick Start

```bash
# 1️⃣ Create virtual environment (optional)
python -m venv .venv && source .venv/bin/activate   # (Windows: .venv\Scripts\activate)

# 2️⃣ Install dependencies
pip install -r requirements.txt

# 3️⃣ Seed database (optional - creates support.db with example FAQs)
python -m app.seed_data

# 4️⃣ Run FastAPI backend
uvicorn app.main:app --reload --port 8000

# 5️⃣ Run Streamlit UI (in another terminal)
cd frontend
streamlit run streamlit_app.py
```

---

## 🌍 Live Deployments

**Backend (FastAPI – Railway):**  
🔗 [https://web-production-b381e.up.railway.app/docs](https://web-production-b381e.up.railway.app/docs)

**Frontend (Streamlit – Cloud):**  
💬 [https://customer-support-ai-agent-k4vwnntjzdtznlgtrhoyxs.streamlit.app/](https://customer-support-ai-agent-k4vwnntjzdtznlgtrhoyxs.streamlit.app/)

---

## ⚙️ Environment Variables

Copy `.env.example` → `.env` and adjust as needed.

```env
MODEL_NAME=distilbert-base-uncased-distilled-squad
FAQ_STRICT_THRESHOLD=0.65
AI_CONFIDENCE_THRESHOLD=0.6
AI_TRY_MIN_THRESHOLD=0.3
TOPK_FOR_AI=3
```

---

## 🔌 REST API Endpoints

| Method | Endpoint | Description |
|--------|-----------|--------------|
| `GET` | `/health` | Health check |
| `POST` | `/ask` | Ask a question (auto detects FAQ → AI → Ticket) |
| `POST` | `/tickets` | Create new ticket manually |
| `GET` | `/tickets` | List all tickets |
| `GET` | `/tickets/{id}` | Retrieve specific ticket |
| `GET` | `/faqs` | Get all FAQs |
| `POST` | `/faqs` | Add a new FAQ |

---

## 🧠 How It Works

1. **Rule-based FAQ Matching** → Fast keyword + fuzzy matching using `rapidfuzz`.  
2. **AI Q&A Model** → Uses Hugging Face `pipeline("question-answering")`.  
3. **Ticket Creation** → If model confidence < threshold, logs query as a new ticket.

---

## 🎨 Streamlit UI Features
- Light & Dark theme compatible.
- Sidebar for API Base URL + Ticket list + Manual ticket form.
- Chat bubbles for user & bot.
- Source badges (FAQ / AI / Ticket) with colors.
- Automatic ticket refresh and error handling.

---

## 🚀 Deployment Guide

### **Procfile**
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### **runtime.txt**
```
python-3.13.3
```

### **requirements.txt**
```
fastapi
uvicorn
sqlalchemy
pydantic
requests
python-dotenv
transformers
torch
rapidfuzz
streamlit
```

### Deployment Options

**✅ Railway (Backend)**  
1. Push to GitHub → Create new Railway project → Select repo.  
2. Add environment variables from `.env`.  
3. Railway auto-detects `Procfile` and starts `uvicorn` server.

**✅ Streamlit Cloud (Frontend)**  
1. Push to GitHub → Create new Streamlit app → Select `frontend/streamlit_app.py`.  
2. In sidebar → Set API Base URL to backend deployment link.

---


