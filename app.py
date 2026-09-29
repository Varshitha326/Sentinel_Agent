import json
import os
from datetime import datetime

import streamlit as st

from sentinel.agent import (
    ask_agent,
    save_incident,
    reflect_and_update_runbook,
    list_memory_items,
    RUNBOOK_PATH,
)
from generate_incidents import generate_and_save

st.set_page_config(page_title="Sentinel", page_icon="🛡️", layout="wide")

LOADED_FLAG = "incidents_loaded.flag"
NEW_LOG = "new_incidents_log.json"

# ---------- Styling ----------
st.markdown(
    """
    <style>
    .block-container {padding-top: 2rem; max-width: 1300px;}
    .hero {
        padding: 1.4rem 1.6rem;
        border-radius: 16px;
        background: linear-gradient(135deg, #1e3a8a 0%, #6d28d9 100%);
        color: white;
        margin-bottom: 1.2rem;
    }
    .hero h1 {margin: 0; font-size: 2.2rem; color: white;}
    .hero p {margin: 0.3rem 0 0 0; opacity: 0.9; font-size: 1.05rem;}
    .step-card {
        padding: 0.9rem 1rem;
        border-radius: 12px;
        border: 1px solid rgba(128,128,128,0.35);
        text-align: center;
    }
    .step-card b {font-size: 1.05rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- State ----------
if "history" not in st.session_state:
    st.session_state.history = []
if "problem_text" not in st.session_state:
    st.session_state.problem_text = ""
if "mem_view" not in st.session_state:
    st.session_state.mem_view = None


# ---------- Helpers ----------
def incidents_already_loaded() -> bool:
    return os.path.exists(LOADED_FLAG)


def runbook_exists() -> bool:
    return os.path.exists(RUNBOOK_PATH)


def runbook_updated_at() -> str:
    ts = os.path.getmtime(RUNBOOK_PATH)
    return datetime.fromtimestamp(ts).strftime("%d %b %Y, %H:%M:%S")


def load_new_log() -> list:
    if not os.path.exists(NEW_LOG):
        return []
    try:
        with open(NEW_LOG, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def append_new_log(entry: dict) -> None:
    log = load_new_log()
    log.append(entry)
    with open(NEW_LOG, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)


# ---------- Sidebar: demo controls ----------
with st.sidebar:
    st.header("🎬 Demo Controls")
    st.caption("Use these in order during the demo.")

    # Step 1: one-time load (no duplicates)
    if incidents_already_loaded():
        st.button("✅ Past incidents already loaded", disabled=True, use_container_width=True)
    elif st.button("1️⃣  Load past incidents", use_container_width=True):
        with st.spinner("Saving incidents into Hindsight memory..."):
            try:
                generate_and_save()
                with open(LOADED_FLAG, "w") as f:
                    f.write("done")
                st.rerun()
            except Exception as e:
                st.error(f"Could not load incidents: {e}")

    # Step 2: reflect
    if st.button("2️⃣  Run Reflect (update runbook)", use_container_width=True):
        with st.spinner("Reflecting across all incidents..."):
            try:
                reflect_and_update_runbook()
                st.success("Runbook updated.")
            except Exception as e:
                st.error(f"Reflect failed: {e}")

    st.markdown("**3️⃣  Ask a question** on the main page.")
    st.markdown("**4️⃣  Click ✅ if the fix worked** so Sentinel remembers it.")

    st.divider()
    if st.button("🗑️ Reset runbook (for a fresh demo)", use_container_width=True):
        if runbook_exists():
            os.remove(RUNBOOK_PATH)
        st.session_state.history = []
        st.rerun()

    with st.expander("ℹ️ How Sentinel works"):
        st.markdown(
            """
            - **Retain:** every incident and its fix is saved to Hindsight memory.
            - **Recall:** for a new problem, Sentinel searches memory for similar past incidents.
            - **Reflect:** Hindsight looks across all incidents, finds repeating patterns, and Sentinel writes them into the runbook.
            """
        )

# ---------- Header ----------
st.markdown(
    """
    <div class="hero">
        <h1>🛡️ Sentinel</h1>
        <p>An on-call assistant that remembers every incident and writes its own runbook, powered by Hindsight memory.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- Status row ----------
new_saved_total = len(load_new_log())

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(
        f"<div class='step-card'>📥 <b>Memory</b><br>"
        f"{'Past incidents loaded ✅' if incidents_already_loaded() else 'Not loaded yet'}"
        f"<br>New incidents saved by you: {new_saved_total}</div>",
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        f"<div class='step-card'>📖 <b>Runbook</b><br>"
        f"{'Updated ' + runbook_updated_at() if runbook_exists() else 'Not generated yet'}</div>",
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        f"<div class='step-card'>💬 <b>Questions asked</b><br>{len(st.session_state.history)}</div>",
        unsafe_allow_html=True,
    )

st.write("")

# ---------- Main: two columns ----------
left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("💬 Ask Sentinel")

    st.caption("Try an example:")
    examples = [
        "checkout-service is throwing 504 errors under heavy load",
        "users can't log in, gateway timeout on the login endpoint",
        "partners are getting SSL handshake failures",
    ]
    for ex in examples:
        if st.button(ex, key=f"ex_{ex}", use_container_width=True):
            st.session_state.problem_text = ex

    problem = st.text_area(
        "Describe a new problem:",
        key="problem_text",
        placeholder="e.g. checkout-service is throwing 504 errors under load",
        height=100,
    )

    if st.button("🔍 Get suggested fix", type="primary", use_container_width=True):
        if not problem.strip():
            st.warning("Please describe a problem first.")
        else:
            with st.spinner("Searching memory and thinking..."):
                try:
                    answer = ask_agent(problem)
                    st.session_state.history.insert(
                        0,
                        {
                            "id": datetime.now().strftime("%H%M%S%f"),
                            "problem": problem,
                            "answer": answer,
                            "saved": False,
                        },
                    )
                except Exception as e:
                    st.error(f"Something went wrong: {e}")

    if st.session_state.history:
        st.markdown("#### Answers")
        for item in st.session_state.history:
            st.markdown(f"**Problem:** {item['problem']}")
            with st.container(border=True):
                st.markdown(item["answer"])

            if item["saved"]:
                st.success("Saved to memory ✅ Sentinel will recall this next time.")
            elif st.button(
                "✅ This fix worked — save to memory",
                key=f"save_{item['id']}",
            ):
                try:
                    today = datetime.now().strftime("%Y-%m-%d")
                    clean_fix = item["answer"].replace("**", "")
                    save_incident(
                        f"Incident on {today}: {item['problem']}. "
                        f"Resolution: {clean_fix}"
                    )
                    append_new_log(
                        {
                            "date": datetime.now().strftime("%d %b %Y, %H:%M"),
                            "problem": item["problem"],
                            "resolution": clean_fix,
                        }
                    )
                    item["saved"] = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not save to memory: {e}")

with right:
    st.subheader("📖 Living Runbook")
    if runbook_exists():
        st.caption(f"🕒 Last updated: {runbook_updated_at()}")
        with open(RUNBOOK_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        # keep table rows intact: turn stray <br> tags into separators
        content = content.replace("<br>", "; ")
        with st.container(border=True, height=600):
            st.markdown(content)
        st.download_button(
            "⬇️ Download runbook.md",
            data=content,
            file_name="runbook.md",
            mime="text/markdown",
        )
    else:
        st.info(
            "No runbook yet. Load the past incidents, then click "
            "**Run Reflect** in the sidebar to generate it."
        )

# ---------- Memory viewer ----------
st.divider()
st.subheader("🧠 What's in memory")
tab_new, tab_all = st.tabs(["🆕 New incidents you saved", "📚 Everything in Hindsight memory"])

with tab_new:
    new_log = load_new_log()
    if not new_log:
        st.info("Nothing saved yet. Ask a question and click ✅ when the fix worked.")
    else:
        for entry in reversed(new_log):
            with st.container(border=True):
                st.markdown(f"**{entry['date']}** — {entry['problem']}")
                st.caption(entry["resolution"])

with tab_all:
    st.caption(
        "Hindsight splits each incident into smaller facts, so this count "
        "will be higher than the number of incidents. New saves can take a few seconds to appear."
    )
    if st.button("🔄 Refresh from Hindsight"):
        with st.spinner("Reading memory..."):
            try:
                st.session_state.mem_view = list_memory_items(limit=100)
            except Exception as e:
                st.error(f"Could not read memory: {e}")
    if st.session_state.mem_view:
        total, texts = st.session_state.mem_view
        st.markdown(f"**Total memory items: {total}** (showing up to {len(texts)})")
        with st.container(border=True, height=350):
            for t in texts:
                st.markdown(f"- {t}")