"""
Streamlit UI: one question, two pipelines, side by side.

Run with:  streamlit run app.py
"""
import streamlit as st

import config
import llm
import okf_pipeline
import rag_pipeline
from questions import QUESTIONS

st.set_page_config(page_title="RAG vs OKF", page_icon="⚖️", layout="wide")

# --- Styling: big, clean, readable on video, works in dark mode ---------------
st.markdown(
    """
<style>
.block-container { padding-top: 2.2rem; max-width: 1700px; }
h1 { font-size: 2.6rem !important; }
.subtitle { font-size: 1.2rem; opacity: .7; margin-top: -.6rem; margin-bottom: 1.2rem; }
.stTextInput input { font-size: 1.45rem !important; padding: .8rem 1rem !important; }
.stTextInput label p { font-size: 1.1rem !important; }
div.stButton > button[kind="primary"] { font-size: 1.3rem; padding: .6rem 2.4rem; }
.col-label {
  font-size: 3rem; font-weight: 800; letter-spacing: .12em; text-align: center;
  border-radius: 16px; padding: .3rem 0; margin-bottom: .3rem;
}
.rag { color: #ffa24c; background: rgba(255,140,0,.13); border: 2px solid rgba(255,140,0,.55); }
.okf { color: #52bdff; background: rgba(0,160,255,.12); border: 2px solid rgba(0,160,255,.55); }
.how { text-align: center; font-size: 1rem; opacity: .65; margin-bottom: 1rem; }
.answer p, .answer li { font-size: 1.3rem !important; line-height: 1.6; }
.time { font-size: 1.5rem; font-weight: 700; margin: .6rem 0 .2rem 0; }
.src { font-family: ui-monospace, Menlo, monospace; font-size: 1.02rem; opacity: .9; }
section[data-testid="stSidebar"] button p { font-size: .98rem; text-align: left; }
</style>
""",
    unsafe_allow_html=True,
)


# --- One-time setup: build the vector index and warm up the model --------------
@st.cache_resource(show_spinner="Building the vector index and loading the model…")
def prepare():
    rag_pipeline.ensure_index()
    llm.warm_up()  # so neither pipeline pays the model-loading cost
    return True


def set_question(q: str):
    st.session_state.question = q


# --- Sidebar: preset demo questions -------------------------------------------
with st.sidebar:
    st.markdown("### Demo questions")
    for label, qtype in (("🎯 Exact questions", "exact"), ("🌊 Open-ended (messy data)", "open-ended")):
        st.markdown(f"**{label}**")
        for q in QUESTIONS:
            if q["type"] == qtype:
                st.button(q["question"], key=f"preset_{q['id']}", on_click=set_question,
                          args=(q["question"],), width="stretch")
    st.divider()
    st.caption(f"Model: **{config.active_model()}** · temperature {config.TEMPERATURE}")
    st.caption("Both pipelines use the same model, settings and answer prompt.")

# --- Header + question box ------------------------------------------------------
st.title("RAG vs OKF")
st.markdown('<div class="subtitle">Same question · same model · two ways to find knowledge</div>',
            unsafe_allow_html=True)

try:
    prepare()
except Exception as e:  # e.g. Ollama not running
    st.error(f"Setup failed: {e}")
    st.stop()

question = st.text_input("Ask a question about Northwind Analytics", key="question",
                         placeholder="e.g. What is the refund window for annual plans?")
ask = st.button("Ask both", type="primary")

st.write("")
col_rag, col_okf = st.columns(2, gap="large")
with col_rag:
    st.markdown('<div class="col-label rag">RAG</div>', unsafe_allow_html=True)
    st.markdown('<div class="how">Vector search over all docs (/raw + /okf) → top 4 chunks → LLM</div>',
                unsafe_allow_html=True)
    rag_slot = st.empty()
with col_okf:
    st.markdown('<div class="col-label okf">OKF</div>', unsafe_allow_html=True)
    st.markdown('<div class="how">LLM reads the OKF index → opens the right file(s) → LLM</div>',
                unsafe_allow_html=True)
    okf_slot = st.empty()


def render(slot, result: dict | None, kind: str):
    """Draw one column's result: answer, time, sources."""
    with slot.container():
        if result is None:
            return
        if "error" in result:
            st.error(result["error"])
            return
        with st.container(border=True):
            st.markdown(f'<div class="answer">\n\n{result["answer"]}\n\n</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="time">⏱ {result["seconds"]:.1f} s</div>', unsafe_allow_html=True)

        st.markdown("**Sources used**")
        if not result["sources"]:
            st.markdown('<div class="src">— none (no OKF file matched)</div>', unsafe_allow_html=True)
        for s in result["sources"]:
            label = f"{s['file']} · chunk {s['chunk']}" if kind == "rag" else s["file"]
            st.markdown(f'<div class="src">📄 {label}</div>', unsafe_allow_html=True)

        with st.expander("Show retrieved text" if kind == "rag" else "Show files read"):
            for s in result["sources"]:
                st.markdown(f"**{s['file']}**")
                st.code(s["text"], language="markdown", wrap_lines=True)
            if kind == "okf":
                st.caption(f"Router reply: {result['router_reply']}")


def run(fn, q: str) -> dict:
    try:
        return fn(q)
    except Exception as e:
        return {"error": str(e)}


# --- Run both pipelines ---------------------------------------------------------
# They run one after the other (not in parallel) so that on a local machine
# neither pipeline slows the other down, which keeps the timings fair.
if ask and question.strip():
    st.session_state.results = {"rag": None, "okf": None}
    with rag_slot.container(), st.spinner("RAG is searching…"):
        st.session_state.results["rag"] = run(rag_pipeline.answer, question)
    render(rag_slot, st.session_state.results["rag"], "rag")
    with okf_slot.container(), st.spinner("OKF is reading…"):
        st.session_state.results["okf"] = run(okf_pipeline.answer, question)
    render(okf_slot, st.session_state.results["okf"], "okf")
elif "results" in st.session_state:
    render(rag_slot, st.session_state.results["rag"], "rag")
    render(okf_slot, st.session_state.results["okf"], "okf")
