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

/* Probe alert */
.probe-alert {
    background: #1a0a00;
    border: 1px solid #7c2d12;
    border-radius: 12px;
    padding: 0.85rem 1.2rem;
    margin-top: 1rem;
    font-size: 0.82rem;
    color: #fb923c;
    font-weight: 600;
    letter-spacing: 0.2px;
}

/* Novelty badge */
.novelty-badge {
    display: inline-block;
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 0.2rem 0.55rem;
    border-radius: 999px;
    margin-left: 0.6rem;
    vertical-align: middle;
}
.novelty-high { background: #4c0519; color: #f43f5e; border: 1px solid #881337; }
.novelty-mid  { background: #1c1200; color: #facc15; border: 1px solid #713f12; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #07090f !important;
    border-right: 1px solid #1e293b !important;
}

.footer { font-size:0.68rem; color:#1e293b; text-align:center; margin-top:2rem; letter-spacing:0.5px; }
</style>
""", unsafe_allow_html=True)


# ── Load model + learner ───────────────────────────────────────────────────────
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

# Session state for probe / candidate tracking
if "candidates" not in st.session_state:
    st.session_state.candidates = []
if "learned" not in st.session_state:
    st.session_state.learned = []
if "probe_count" not in st.session_state:
    st.session_state.probe_count = 0


# ── Admin sidebar ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🛡️ Attack Learning Panel")
    st.caption(f"ChromaDB vectors loaded: **{learner.collection_size()}**")

    if st.session_state.candidates:
        st.markdown("#### ⏳ Pending Review")
        for item in list(st.session_state.candidates):
            p   = item["prompt"]
            risk = item["risk_score"]
            nov  = item.get("novelty_score", 0.0)

            # Novelty badge label
            if nov > 0.5:
                nov_label = f'<span class="novelty-badge novelty-high">🆕 Novel {int(nov*100)}%</span>'
            elif nov > 0.2:
                nov_label = f'<span class="novelty-badge novelty-mid">Variant {int(nov*100)}%</span>'
            else:
                nov_label = ""

            st.markdown(
                f'<div style="font-size:0.78rem;color:#94a3b8;margin-bottom:0.3rem;">'
                f'<b style="color:#e2e8f0">{p[:55]}{"…" if len(p)>55 else ""}</b>'
                f'{nov_label}<br/>'
                f'<span style="color:#475569">Risk {int(risk*100)}% · {item["timestamp"]}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Approve", key=f"approve_{p[:20]}"):
                    stats = learner.approve(p)
                    # Sync session state
                    st.session_state.candidates = [
                        c for c in st.session_state.candidates if c["prompt"] != p
                    ]
                    st.session_state.learned.append({
                        **stats,
                        "timestamp": item["timestamp"]
                    })
                    st.success(f"Added + {stats['variants_added']} variants to ChromaDB")
                    st.rerun()
            with col2:
                if st.button("❌ Reject", key=f"reject_{p[:20]}"):
                    learner.reject(p)
                    st.session_state.candidates = [
                        c for c in st.session_state.candidates if c["prompt"] != p
                    ]
                    st.rerun()
    else:
        st.caption("No candidates pending.")

    if st.session_state.learned:
        st.markdown("#### ✅ Learned This Session")
        for item in st.session_state.learned[-5:]:
            p = item.get("approved", item.get("prompt", ""))
            v = item.get("variants_added", 0)
            st.markdown(
                f'<div style="font-size:0.75rem;color:#475569;margin-bottom:0.3rem;">'
                f'<span style="color:#10b981">✓</span> {p[:45]}{"…" if len(p)>45 else ""}'
                f' <span style="color:#334155">(+{v} variants)</span></div>',
                unsafe_allow_html=True,
            )

        st.markdown("---")
        export_txt = learner.export_learned()
        if export_txt:
            st.download_button(
                "📥 Download learned_attacks.txt",
                data=export_txt,
                file_name="learned_attacks.txt",
                mime="text/plain",
            )

    st.markdown("---")
    st.markdown("#### 📤 Bulk Import")
    bulk = st.text_area("Paste attack phrases (one per line)", height=100, key="bulk_import")
    if st.button("Import", key="import_btn"):
        if bulk.strip():
            added = learner.import_from_text(bulk)
            st.success(f"Imported {added} patterns into ChromaDB.")
        else:
            st.warning("Nothing to import.")


# ── Main layout ───────────────────────────────────────────────────────────────
st.markdown('<div class="brand">AI Security</div>', unsafe_allow_html=True)
st.markdown('<div class="headline">LLM Guardian</div>', unsafe_allow_html=True)
st.markdown('<div class="tagline">Detect jailbreak and manipulation attempts before they reach your AI.</div>', unsafe_allow_html=True)

prompt = st.text_area("prompt", height=140,
                       placeholder="Paste or type a prompt to inspect...",
                       label_visibility="collapsed")

clicked = st.button("Inspect Prompt")

# ── Result ─────────────────────────────────────────────────────────────────────
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

        # ── Novelty score: how "new" is this attack?
        # High similarity to known attacks → low novelty (we've seen it before)
        # Low similarity but still blocked → high novelty (new attack vector)
        p2_score = result["phase2"]["score"]    # similarity to known attacks (0–1)
        novelty  = round(max(0.0, 1.0 - p2_score), 3)  # inverse of similarity

        if verdict == "BLOCK":
            vcard, vstatus, vtitle_cls, vfill, vpct_cls = \
                "verdict-danger", "v-status-danger", "v-title-danger", "rbar-fill-danger", "rbar-pct-danger"
            status_txt = "Blocked"
            title_txt  = "Access Denied"
            desc_txt   = "This prompt has been identified as a threat and has been blocked."

            # ── Auto-queue as candidate + probe detection
            is_probing = learner.record_block(prompt.strip(), risk)
            st.session_state.probe_count = learner.probe_count()

            # Add to candidate queue if not already known
            learner.add_candidate(prompt.strip(), risk, novelty)
            st.session_state.candidates = learner.get_candidates()

        elif verdict == "ALLOW":
            vcard, vstatus, vtitle_cls, vfill, vpct_cls = \
                "verdict-safe", "v-status-safe", "v-title-safe", "rbar-fill-safe", "rbar-pct-safe"
            status_txt = "Clear"
            title_txt  = "Safe to Send"
            desc_txt   = "No suspicious patterns detected. This prompt is clean and safe to forward to the AI model."
            novelty    = 0.0
        else:
            vcard, vstatus, vtitle_cls, vfill, vpct_cls = \
                "verdict-review", "v-status-review", "v-title-review", "rbar-fill-review", "rbar-pct-review"
            status_txt = "Suspicious — Blocked"
            title_txt  = "Access Restricted"
            desc_txt   = "Unusual patterns detected. As a precaution, you have been blocked."

            learner.record_block(prompt.strip(), risk)
            st.session_state.probe_count = learner.probe_count()
            learner.add_candidate(prompt.strip(), risk, novelty)
            st.session_state.candidates = learner.get_candidates()

        # ── Novelty badge HTML
        if novelty > 0.5 and verdict != "ALLOW":
            novelty_badge = f'<span class="novelty-badge novelty-high">🆕 Novel Attack · {int(novelty*100)}% unseen</span>'
        elif novelty > 0.2 and verdict != "ALLOW":
            novelty_badge = f'<span class="novelty-badge novelty-mid">Variant · {int(novelty*100)}% unseen</span>'
        else:
            novelty_badge = ""

        st.markdown(f"""
        <div class="verdict {vcard}">
            <div class="v-status {vstatus}">{status_txt}{novelty_badge}</div>
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

        # ── Adversarial probing alert
        if st.session_state.probe_count >= 3:
            st.markdown(
                f'<div class="probe-alert">⚠️ Adversarial probing detected — '
                f'<b>{st.session_state.probe_count} blocked attempts</b> this session. '
                f'This session has been flagged for review.</div>',
                unsafe_allow_html=True,
            )

        # ── Sidebar hint on first block
        if verdict in ("BLOCK", "REVIEW") and len(st.session_state.candidates) == 1:
            st.info("💡 Blocked prompt queued in **🛡️ Admin panel** (left sidebar) — approve to permanently expand the attack database.", icon="🛡️")

st.markdown('<div class="footer">LLM Guardian V2 &nbsp;·&nbsp; 3-Phase AI Firewall &nbsp;·&nbsp; Self-Learning</div>', unsafe_allow_html=True)