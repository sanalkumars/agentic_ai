"""
app.py — Streamlit front-end for the multi-agent research pipeline
(Search Agent -> Reader Agent -> Writer Chain -> Critic Chain)

Run with:  streamlit run app.py
"""

import time
from datetime import datetime

import streamlit as st

from pipeline import run_research_pipeline


# ----------------------------------------------------------------------------
# Page config
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Deep Research Pipeline",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------------
# Theme — deep ink background, brass/amber accent, editorial serif for
# headings paired with a clean mono for the "agent trace" feel.
# ----------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --ink: #0f1115;
    --panel: #171a21;
    --panel-2: #1d212b;
    --line: #2a2f3a;
    --brass: #d4a24c;
    --brass-soft: rgba(212, 162, 76, 0.14);
    --teal: #4ea8a0;
    --text: #e9e7e0;
    --text-dim: #9aa0ac;
}

html, body, [class*="css"]  {
    background-color: var(--ink) !important;
    color: var(--text);
    font-family: 'JetBrains Mono', monospace;
}

.stApp {
    background:
        radial-gradient(circle at 15% 0%, rgba(212,162,76,0.06), transparent 40%),
        radial-gradient(circle at 85% 100%, rgba(78,168,160,0.07), transparent 45%),
        var(--ink);
}

/* ---- Hero ---- */
.hero {
    padding: 2.2rem 2.4rem;
    margin-bottom: 1.6rem;
    border: 1px solid var(--line);
    border-radius: 4px;
    background: linear-gradient(135deg, var(--panel) 0%, var(--panel-2) 100%);
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: "";
    position: absolute;
    top: -40%; right: -10%;
    width: 260px; height: 260px;
    border: 1px solid rgba(212,162,76,0.25);
    border-radius: 50%;
}
.hero-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    font-size: 0.72rem;
    color: var(--brass);
    margin-bottom: 0.6rem;
}
.hero-title {
    font-family: 'Fraunces', serif;
    font-weight: 700;
    font-size: 2.6rem;
    line-height: 1.05;
    color: var(--text);
    margin: 0;
}
.hero-sub {
    color: var(--text-dim);
    max-width: 620px;
    margin-top: 0.8rem;
    font-size: 0.92rem;
    line-height: 1.5;
}

/* ---- Pipeline trace ---- */
.stage-row {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.55rem 0.9rem;
    border-radius: 4px;
    border: 1px solid var(--line);
    background: var(--panel);
    margin-bottom: 0.5rem;
    font-size: 0.85rem;
}
.stage-dot {
    width: 9px; height: 9px; border-radius: 50%;
    flex-shrink: 0;
}
.dot-pending { background: #444a58; }
.dot-active { background: var(--brass); box-shadow: 0 0 0 4px var(--brass-soft); }
.dot-done { background: var(--teal); }

/* ---- Cards / panels ---- */
.panel {
    border: 1px solid var(--line);
    background: var(--panel);
    border-radius: 4px;
    padding: 1.4rem 1.5rem;
}
.panel-label {
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    font-size: 0.7rem;
    color: var(--teal);
    margin-bottom: 0.7rem;
}

/* Report body should read like editorial prose */
.report-body, .report-body p, .report-body li {
    font-family: 'Fraunces', serif;
    font-size: 1.02rem;
    line-height: 1.65;
    color: #f0eee6;
}
.report-body h1, .report-body h2, .report-body h3 {
    font-family: 'Fraunces', serif;
    color: var(--brass);
}

hr { border-color: var(--line) !important; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: var(--panel);
    border-right: 1px solid var(--line);
}

/* Buttons */
.stButton>button {
    background: var(--brass);
    color: #1a1508;
    border: none;
    font-weight: 600;
    letter-spacing: 0.03em;
    border-radius: 3px;
    padding: 0.55rem 1.2rem;
}
.stButton>button:hover {
    background: #e3b562;
    color: #1a1508;
}

/* Tabs */
button[data-baseweb="tab"] {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    letter-spacing: 0.02em;
}

.footer-note {
    color: var(--text-dim);
    font-size: 0.75rem;
    margin-top: 2rem;
    border-top: 1px solid var(--line);
    padding-top: 0.8rem;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# Session state
# ----------------------------------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []          # list of {topic, timestamp, state}
if "current" not in st.session_state:
    st.session_state.current = None
if "running" not in st.session_state:
    st.session_state.running = False


# ----------------------------------------------------------------------------
# Sidebar — controls
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🧭 Control Deck")
    st.caption("Search Agent → Reader Agent → Writer → Critic")

    topic = st.text_area(
        "Research topic",
        placeholder="e.g. Impact of small modular reactors on grid decarbonization",
        height=100,
    )

    run_clicked = st.button("▶  Run Pipeline", use_container_width=True, disabled=st.session_state.running)

    st.divider()
    st.markdown("### 🗂 Past Runs")
    if not st.session_state.history:
        st.caption("No runs yet this session.")
    else:
        for i, item in enumerate(reversed(st.session_state.history)):
            idx = len(st.session_state.history) - 1 - i
            label = f"{item['topic'][:32]}{'…' if len(item['topic']) > 32 else ''}"
            if st.button(label, key=f"hist_{idx}", use_container_width=True):
                st.session_state.current = st.session_state.history[idx]

    st.markdown(
        '<div class="footer-note">Runs are synchronous — each pipeline call '
        "invokes your live agents, so expect real API latency.</div>",
        unsafe_allow_html=True,
    )


# ----------------------------------------------------------------------------
# Hero
# ----------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <div class="hero-eyebrow">Multi-Agent Research Desk</div>
        <div class="hero-title">Deep Research Pipeline</div>
        <div class="hero-sub">
            One topic in, four agents at work: a Search Agent scouts the web,
            a Reader Agent scrapes the most relevant source, a Writer drafts
            the report, and a Critic reviews it before you see the final cut.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------------------
# Run the pipeline
# ----------------------------------------------------------------------------
STAGES = [
    ("search", "🔎", "Search Agent — scanning the web"),
    ("scrape", "📖", "Reader Agent — scraping the top source"),
    ("write", "✍️", "Writer Chain — drafting the report"),
    ("critique", "🧐", "Critic Chain — reviewing the draft"),
]

if run_clicked:
    if not topic or not topic.strip():
        st.warning("Enter a research topic before running the pipeline.")
    else:
        st.session_state.running = True
        trace_ph = st.empty()

        def render_trace(active_idx):
            rows = ""
            for i, (_, icon, label) in enumerate(STAGES):
                if i < active_idx:
                    dot = "dot-done"
                elif i == active_idx:
                    dot = "dot-active"
                else:
                    dot = "dot-pending"
                rows += (
                    f'<div class="stage-row"><span class="stage-dot {dot}"></span>'
                    f"{icon} {label}</div>"
                )
            trace_ph.markdown(rows, unsafe_allow_html=True)

        # We can't get true intermediate callbacks from run_research_pipeline
        # without editing pipeline.py, so we show a lightweight simulated
        # trace alongside a real spinner while the actual (blocking) call runs.
        render_trace(0)
        with st.spinner("Agents are working — this calls your live pipeline..."):
            start = time.time()
            result_state = run_research_pipeline(topic=topic.strip())
            elapsed = time.time() - start
        render_trace(len(STAGES))

        run_record = {
            "topic": topic.strip(),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "elapsed": round(elapsed, 1),
            "state": result_state,
        }
        st.session_state.history.append(run_record)
        st.session_state.current = run_record
        st.session_state.running = False
        st.success(f"Pipeline complete in {run_record['elapsed']}s")


# ----------------------------------------------------------------------------
# Results
# ----------------------------------------------------------------------------
current = st.session_state.current

if current is None:
    st.markdown(
        """
        <div class="panel">
        <div class="panel-label">Awaiting input</div>
        Enter a topic in the sidebar and hit <b>Run Pipeline</b> to see the
        search results, scraped source, drafted report, and critic feedback here.
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    state = current["state"]

    st.caption(
        f"Topic: **{current['topic']}**  ·  Run at {current['timestamp']}  ·  "
        f"{current['elapsed']}s"
    )

    tab_report, tab_critic, tab_search, tab_scrape = st.tabs(
        ["📄 Final Report", "🧐 Critic Feedback", "🔎 Search Results", "📖 Scraped Content"]
    )

    with tab_report:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-label">Writer Chain Output</div>', unsafe_allow_html=True)
        report_text = state.get("report", "_No report generated._")
        report_text = report_text if isinstance(report_text, str) else str(report_text)
        st.markdown(f'<div class="report-body">{report_text}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.download_button(
            "⬇ Download report (.md)",
            data=report_text,
            file_name=f"report_{current['topic'][:30].replace(' ', '_')}.md",
            mime="text/markdown",
        )

    with tab_critic:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-label">Critic Chain Output</div>', unsafe_allow_html=True)
        feedback_text = state.get("feedback", "_No feedback generated._")
        feedback_text = feedback_text if isinstance(feedback_text, str) else str(feedback_text)
        st.markdown(f'<div class="report-body">{feedback_text}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_search:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-label">Search Agent Output</div>', unsafe_allow_html=True)
        st.text(state.get("search_result", "No search result captured."))
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_scrape:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-label">Reader Agent Output</div>', unsafe_allow_html=True)
        st.text(state.get("scrape_result", "No scraped content captured."))
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    '<div class="footer-note">Deep Research Pipeline · Streamlit UI over '
    "agents.py + pipeline.py</div>",
    unsafe_allow_html=True,
)