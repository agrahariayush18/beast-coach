import streamlit as st
from beast_coach import answer

# ---------- page config ----------
st.set_page_config(
    page_title="Beast Coach — AI Supplement Advisor",
    page_icon="🦁",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ---------- custom styling ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600;800&family=Inter:wght@400;500;600&display=swap');

/* hide Streamlit's default chrome for a clean product look */
header[data-testid="stHeader"] {background: transparent;}
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] {visibility: hidden;}

/* app background with a soft accent glow at the top */
.stApp {
    background:
        radial-gradient(1100px 500px at 50% -15%, rgba(255,90,45,0.14), transparent 60%),
        #0B0B0F;
    font-family: 'Inter', sans-serif;
}

/* hero */
.hero-title {
    font-family: 'Poppins', sans-serif;
    font-weight: 800;
    font-size: 3rem;
    line-height: 1.05;
    letter-spacing: -1px;
    background: linear-gradient(90deg, #FF8A3D 0%, #FF3D6E 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.3rem;
}
.hero-sub { color: #A8A8B3; font-size: 1.05rem; margin-bottom: 0.6rem; }
.hero-badge {
    display: inline-block; padding: 5px 13px; border-radius: 999px;
    border: 1px solid rgba(255,255,255,0.12); background: rgba(255,255,255,0.04);
    color: #C9C9D2; font-size: 0.76rem; letter-spacing: 0.3px;
}

/* chat bubbles */
[data-testid="stChatMessage"] {
    background: #14141A; border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px; padding: 14px 16px; margin-bottom: 8px;
}

/* suggestion chips (buttons) */
.stButton > button {
    width: 100%; text-align: left;
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.10);
    color: #D7D7DE; border-radius: 14px; padding: 14px 16px;
    font-size: 0.92rem; transition: all 0.15s ease;
}
.stButton > button:hover {
    border-color: #FF5A2D; color: #FFFFFF;
    box-shadow: 0 0 0 1px rgba(255,90,45,0.45); transform: translateY(-1px);
}

/* sidebar */
[data-testid="stSidebar"] {
    background: #0E0E13; border-right: 1px solid rgba(255,255,255,0.05);
}
</style>
""", unsafe_allow_html=True)

# ---------- hero header ----------
st.markdown("""
<div class="hero-title">🦁 Beast Coach</div>
<div class="hero-sub">Your AI supplement advisor — grounded in BeastLife's real catalog.</div>
<span class="hero-badge">⚡ Powered by RAG · Groq LLaMA 3.3 · grounded, no hallucinations</span>
""", unsafe_allow_html=True)
st.write("")

# ---------- sidebar ----------
with st.sidebar:
    st.markdown("### 🦁 Beast Coach")
    st.caption("An AI advisor that recommends the right BeastLife supplements for your "
               "goal — and answers product, usage, and policy questions.")
    st.markdown("---")
    st.markdown("**What I can help with**")
    st.markdown("- 🏋️ Pick the right supplement for your goal\n"
                "- 💊 Dosage & timing\n"
                "- 🌱 Veg / lactose-friendly options\n"
                "- 🚚 Shipping, returns & payment")
    st.markdown("---")
    st.caption("⚠️ Not medical advice. For health conditions, pregnancy, or under-18, "
               "consult a doctor.")
    st.caption("Built by Ayush Agrahari")

# ---------- session state ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------- welcome suggestions (only before the first message) ----------
clicked = None
if not st.session_state.messages:
    st.markdown("##### Try asking 👇")
    suggestions = [
        "I'm a beginner — what should I take to build muscle?",
        "When should I take creatine?",
        "Do you have a vegetarian protein?",
        "What's your return policy?",
    ]
    c1, c2 = st.columns(2)
    for i, s in enumerate(suggestions):
        col = c1 if i % 2 == 0 else c2
        if col.button(s, key=f"sugg_{i}"):
            clicked = s

# ---------- render conversation history ----------
for msg in st.session_state.messages:
    avatar = "🦁" if msg["role"] == "assistant" else "🧑"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"], unsafe_allow_html=True)

# ---------- handle input (typed OR a clicked chip) ----------
typed = st.chat_input("Ask me anything about BeastLife supplements...")
prompt = clicked or typed

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.spinner("Beast Coach is thinking..."):
        reply, sources = answer(prompt)
    if sources:
        unique = list(dict.fromkeys(sources))
        reply += (f"\n\n<span style='font-size:0.8rem;color:#8A8A95;'>"
                  f"📚 Sources: {', '.join(unique)}</span>")
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()