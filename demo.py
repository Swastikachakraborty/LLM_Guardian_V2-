import streamlit as st
import time

st.set_page_config(page_title="LLM Guardian", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #050508; }
#MainMenu, footer, header { display: none !important; }
.block-container { padding-top: 0 !important; padding-bottom: 0 !important; max-width: 600px !important; }
section[data-testid="stSidebar"] { display: none !important; }

/* Page center */
.page {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 3rem 1.5rem;
}

/* Header */
.brand {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #334155;
    text-align: center;
    margin-bottom: 0.6rem;
}
.headline {
    font-size: 3rem;
    font-weight: 900;
    letter-spacing: -2px;
    color: #e2e8f0;
    text-align: center;
    line-height: 1;
    margin-bottom: 0.4rem;
}
.tagline {
    font-size: 0.88rem;
    color: #334155;
    text-align: center;
    margin-bottom: 2.5rem;
    font-weight: 400;
}

/* Input */
.stTextArea textarea {
    background: #0a0d14 !important;
    border: 1px solid #1e293b !important;
    border-radius: 14px !important;
    color: #cbd5e1 !important;
    font-size: 0.97rem !important;
    font-family: 'Inter', sans-serif !important;
    padding: 1rem 1.2rem !important;
    resize: none !important;
    line-height: 1.65 !important;
    transition: border-color 0.25s !important;
}
.stTextArea textarea:focus {
    border-color: #6366f1 !important;
    box-shadow: none !important;
}
.stTextArea textarea::placeholder { color: #1e293b !important; }
.stTextArea label { display: none !important; }

/* Button */
.stButton > button {
    width: 100% !important;
    background: #6366f1 !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-size: 0.92rem !important;
    font-weight: 600 !important;
    padding: 0.8rem !important;
    letter-spacing: 0.3px !important;
    margin-top: 0.5rem !important;
    transition: background 0.2s, transform 0.15s !important;
    box-shadow: none !important;
}
.stButton > button:hover {
    background: #4f46e5 !important;
    transform: translateY(-1px) !important;
}

/* Verdict */
.verdict {
    width: 100%;
    border-radius: 16px;
    padding: 2rem 1.8rem;
    margin-top: 1.5rem;
    animation: up 0.3s ease;
}
.verdict-safe   { background: #051a10; border: 1px solid #064e29; }
.verdict-danger { background: #1a0505; border: 1px solid #4e0606; }
.verdict-review { background: #1a1205; border: 1px solid #4e3206; }
@keyframes up { from{opacity:0;transform:translateY(10px)} to{opacity:1;transform:translateY(0)} }

.v-status {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.v-status-safe   { color: #10b981; }
.v-status-danger { color: #ef4444; }
.v-status-review { color: #f59e0b; }

.v-title {
    font-size: 1.9rem;
    font-weight: 900;
    letter-spacing: -1px;
    margin-bottom: 0.5rem;
    line-height: 1.1;
}
.v-title-safe   { color: #e2e8f0; }
.v-title-danger { color: #e2e8f0; }
.v-title-review { color: #e2e8f0; }

.v-desc {
    font-size: 0.85rem;
    color: #475569;
    line-height: 1.55;
    margin-bottom: 1.2rem;
}

/* Risk bar */
.rbar-row { display:flex; align-items:center; gap:0.6rem; }
.rbar-label { font-size:0.7rem; color:#334155; font-weight:600; letter-spacing:0.5px; text-transform:uppercase; min-width:28px; }
.rbar-track { flex:1; height:4px; background:#1e293b; border-radius:999px; overflow:hidden; }
.rbar-fill-safe   { height:100%; border-radius:999px; background:#10b981; }
.rbar-fill-danger { height:100%; border-radius:999px; background:#ef4444; }
.rbar-fill-review { height:100%; border-radius:999px; background:#f59e0b; }
.rbar-pct { font-size:0.78rem; font-weight:700; min-width:32px; text-align:right; }
.rbar-pct-safe   { color:#10b981; }
.rbar-pct-danger { color:#ef4444; }
.rbar-pct-review { color:#f59e0b; }

.footer { font-size:0.68rem; color:#1e293b; text-align:center; margin-top:2rem; letter-spacing:0.5px; }
</style>
""", unsafe_allow_html=True)


# ── Load model ────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_guardian():
    from detector import LLMGuardian
    return LLMGuardian()

@st.cache_resource(show_spinner=False)
def load_learner(_guardian):
    from attack_learner import AttackLearner
    return AttackLearner(_guardian.phase2)

with st.spinner(""):
    guardian = load_guardian()
    learner  = load_learner(guardian)


# ── Layout ────────────────────────────────────────────────────────────────────
st.markdown('<div class="brand">AI Security</div>', unsafe_allow_html=True)
st.markdown('<div class="headline">LLM Guardian</div>', unsafe_allow_html=True)
st.markdown('<div class="tagline">Detect jailbreak and manipulation attempts before they reach your AI.</div>', unsafe_allow_html=True)

prompt = st.text_area("prompt", height=140,
                       placeholder="Paste or type a prompt to inspect...",
                       label_visibility="collapsed")

clicked = st.button("Inspect Prompt")

# ── Result ────────────────────────────────────────────────────────────────────
if clicked:
    if not prompt.strip():
        st.warning("Please enter a prompt first.")
    else:
        pb = st.progress(0)
        status = st.empty()
        status.markdown('<p style="color:#334155;font-size:0.8rem;">Scanning...</p>', unsafe_allow_html=True)
        for i in range(1, 101):
            time.sleep(0.006)
            pb.progress(i)
        pb.empty()
        status.empty()

        result  = guardian.analyze(prompt.strip())
        verdict = result["verdict"]
        risk    = result["risk_score"]
        pct     = int(risk * 100)

        # ── Background: auto-queue blocked prompts (silent, no UI change)
        if verdict in ("BLOCK", "REVIEW"):
            p2_score = result["phase2"]["score"]
            novelty  = round(max(0.0, 1.0 - p2_score), 3)
            learner.record_block(prompt.strip(), risk)
            learner.add_candidate(prompt.strip(), risk, novelty)

        if verdict == "BLOCK":
            vcard, vstatus, vtitle_cls, vfill, vpct_cls = \
                "verdict-danger", "v-status-danger", "v-title-danger", "rbar-fill-danger", "rbar-pct-danger"
            status_txt = "Blocked"
            title_txt  = "Access Denied"
            desc_txt   = "This prompt has been identified as a threat and has been blocked. If you believe this is a mistake, please contact the administrator."
        elif verdict == "ALLOW":
            vcard, vstatus, vtitle_cls, vfill, vpct_cls = \
                "verdict-safe", "v-status-safe", "v-title-safe", "rbar-fill-safe", "rbar-pct-safe"
            status_txt = "Clear"
            title_txt  = "Safe to Send"
            desc_txt   = "No suspicious patterns detected. This prompt is clean and safe to forward to the AI model."
        else:
            vcard, vstatus, vtitle_cls, vfill, vpct_cls = \
                "verdict-review", "v-status-review", "v-title-review", "rbar-fill-review", "rbar-pct-review"
            status_txt = "Suspicious — Blocked"
            title_txt  = "Access Restricted"
            desc_txt   = "Unusual patterns detected. As a precaution, you have been blocked. If you believe this is a mistake, please contact the administrator."

        st.markdown(f"""
        <div class="verdict {vcard}">
            <div class="v-status {vstatus}">{status_txt}</div>
            <div class="v-title {vtitle_cls}">{title_txt}</div>
            <div class="v-desc">{desc_txt}</div>
            <div class="rbar-row">
                <span class="rbar-label">Risk</span>
                <div class="rbar-track">
                    <div class="{vfill}" style="width:{pct}%"></div>
                </div>
                <span class="rbar-pct {vpct_cls}">{pct}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('<div class="footer">LLM Guardian V2 &nbsp;·&nbsp; 3-Phase AI Firewall</div>', unsafe_allow_html=True)