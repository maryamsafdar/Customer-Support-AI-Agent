import requests
import streamlit as st
import os

# ── MUST be first Streamlit call ───────────────────────────────────────────────
st.set_page_config(page_title="Support AI Agent", page_icon="💬", layout="wide")

# ── Helpers ───────────────────────────────────────────────────────────────────
def get_base_url():
    return st.session_state.get("base_url") or os.getenv("BASE_URL", "https://web-production-b381e.up.railway.app/")

def api_post(path: str, json: dict):
    url = f"{get_base_url()}{path}"
    return requests.post(url, json=json, timeout=30)

def api_get(path: str):
    url = f"{get_base_url()}{path}"
    return requests.get(url, timeout=30)

def source_badge(source: str) -> str:
    s = (source or "").lower()
    color = "#888"
    label = s.upper() if s else "UNKNOWN"
    if s == "faq":
        color = "#22c55e"  # green
    elif s == "ai":
        color = "#3b82f6"  # blue
    elif s == "ticket":
        color = "#ef4444"  # red
    return f"<span class='badge' style='background:{color}'>{label}</span>"

# ── Styles ────────────────────────────────────────────────────────────────────
# ── Styles ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Global light theme background */
body, .stApp {
  background-color: #f9fafb;
  color: #111827;
  font-family: "Inter", sans-serif;
}

/* Chat bubbles */
.msg {
  padding:0.8rem 1rem;
  border-radius:12px;
  margin-bottom:0.4rem;
}
.user {
  background:#e6f7ec;  /* soft green tint */
  border:1px solid #bbf7d0; /* light green border */
}
.bot {
  background:#f5f5f5;
  border:1px solid #e5e7eb;
}

/* Badges */
.badge {
  display:inline-block;
  padding:2px 8px;
  border-radius:999px;
  font-size:12px;
  font-weight:600;
  color:#fff;
  vertical-align:middle;
}
.badge[data-source="faq"] {
  background:#16a34a; /* green */
}
.badge[data-source="ai"] {
  background:#3b82f6; /* blue */
}
.badge[data-source="ticket"] {
  background:#dc2626; /* red */
}

/* Metadata */
.small {
  font-size:0.8rem;
  color:#4b5563;
}
.meta {
  display:flex;
  gap:.5rem;
  align-items:center;
  margin-top:.25rem;
}
.hr {
  height:1px;
  background:#d1d5db;
  margin:.5rem 0;
}

/* Sidebar */
section[data-testid="stSidebar"] {
  background-color:#ffffff;
  border-right:2px solid #bbf7d0; /* green accent */
}
</style>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    base_url = st.text_input("API Base URL", value=os.getenv("BASE_URL", "http://localhost:8000"))
    st.session_state["base_url"] = base_url

    st.markdown("---")
    st.subheader("📨 Open Tickets")

    # Load tickets function so we can refresh on demand
    def load_tickets():
        try:
            r = api_get("/tickets")
            if r.ok:
                return r.json()
        except Exception:
            return None
        return None

    tickets = load_tickets()

    if tickets is None:
        st.warning("Tickets unavailable. Check API URL.")
    elif not tickets:
        st.caption("No open tickets.")
    else:
        for t in tickets[:10]:
            # Handle projects where 'status' field doesn't exist by defaulting to 'open'
            status = t.get("status", "open")
            name = t.get("name") or "N/A"
            question = (t.get("question") or "").strip()
            short_q = (question[:60] + "…") if len(question) > 60 else question
            st.write(f"**#{t['id']}** — {short_q}")
            st.caption(f"Status: {status}  |  From: {name}")
            st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

    st.button("↻ Refresh tickets", on_click=lambda: None)

    st.markdown("---")
    st.subheader("📝 Create Manual Ticket")
    with st.form("manual_ticket"):
        q = st.text_area("Issue", placeholder="Describe the customer problem…")
        name = st.text_input("Name (optional)")
        email = st.text_input("Email (optional)")
        submit = st.form_submit_button("Create ticket")
        if submit and q.strip():
            try:
                resp = api_post("/tickets", {"question": q.strip(), "name": name or None, "email": email or None})
                if resp.ok:
                    st.success(f"Ticket #{resp.json()['id']} created.")
                    # soft refresh by re-running app so sidebar shows new ticket
                    st.rerun()
                else:
                    st.error(f"Error: {resp.text}")
            except Exception as e:
                st.error(f"Failed: {e}")

# ── Main ──────────────────────────────────────────────────────────────────────
st.title("💬 Customer Support AI Agent")
st.caption("Ask a question. The agent answers via FAQs → AI → Ticket fallback.")

if "history" not in st.session_state:
    st.session_state.history = []

col_left, col_right = st.columns([3, 1])
with col_right:
    if st.button("🧹 Clear chat"):
        st.session_state.history = []
        st.rerun()

# Chat input
user_input = st.chat_input("Type your question…")
if user_input:
    st.session_state.history.append(("user", user_input))
    with st.spinner("Thinking…"):
        try:
            r = api_post("/ask", {"question": user_input})
            if r.ok:
                res = r.json()
                source = res.get("source")
                score = res.get("score")
                ticket_id = res.get("ticket_id")
                ans = res.get("answer") or ""

                # Build meta line with badge and numbers
                meta_bits = [source_badge(source)]
                if score is not None:
                    meta_bits.append(f"<span class='small'>score: {score:.3f}</span>")
                if ticket_id:
                    meta_bits.append(f"<span class='small'>ticket: #{ticket_id}</span>")
                meta_html = " ".join(meta_bits)

                st.session_state.history.append(("bot", ans, meta_html))

                # If a ticket was created, re-run so the sidebar refreshes
                if source == "ticket":
                    st.rerun()
            else:
                st.session_state.history.append(("bot", f"API error: {r.text}", "<span class='badge' style='background:#f59e0b'>ERROR</span>"))
        except Exception as e:
            st.session_state.history.append(("bot", f"Failed to reach API: {e}", "<span class='badge' style='background:#f59e0b'>ERROR</span>"))

# Render chat
for item in st.session_state.history:
    role = item[0]
    if role == "user":
        with st.chat_message("user"):
            st.markdown(f"<div class='msg user'>{item[1]}</div>", unsafe_allow_html=True)
    else:
        with st.chat_message("assistant"):
            st.markdown(f"<div class='msg bot'>{item[1]}</div>", unsafe_allow_html=True)
            if len(item) > 2 and item[2]:
                st.markdown(f"<div class='meta'>{item[2]}</div>", unsafe_allow_html=True)
