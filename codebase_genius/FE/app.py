"""
Purpose: Streamlit frontend for Codebase Genius.
Connects to Jac backend (Supervisor walker) to visualize repository
documentation generation steps interactively.

Frontend Responsibilities:
 - Accept a GitHub URL as input.
 - Display real-time step-based progress.
 - Render generated documentation (overview + chapters).
 - Allow downloading the tutorial in Markdown format.
"""

import streamlit as st
import requests
from typing import List, Dict, Any

# --- Streamlit Configuration ---
st.set_page_config(page_title="Codebase Genius", page_icon="", layout="wide")
BACKEND_URL = "http://localhost:8000/walker/Supervisor"

# ---------- Helpers ----------
def call_jac_supervisor(repo_url: str) -> Dict[str, Any]:
    """
    Calls the Jac backend Supervisor walker with the provided GitHub URL.
    Returns a dictionary containing tutorial chapters and summary.
    """
    payload = {"repo_url": repo_url}
    r = requests.post(BACKEND_URL, json=payload, timeout=600)
    r.raise_for_status()
    data = r.json()
    reports = data.get("reports", [])
    chapters = None
    summary = None
    for rep in reports:
        if "overview" in rep:
            summary = rep["overview"]
    for rep in reports:
        if "tutorial" in rep:
            chapters = rep["tutorial"]
            break
    return {"chapters": chapters , "summary": summary}


def normalize_chapters(raw: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Normalizes backend chapter objects for frontend rendering."""
    norm = []
    for item in raw:
        ctx = item.get("context", {}) if isinstance(item, dict) else {}
        title = ctx.get("title") or item.get("title") if isinstance(item, dict) else "Untitled"
        content = ctx.get("content") or item.get("content") or ""
        norm.append({"title": title, "content": content})
    return norm


def slugify(title: str) -> str:
    """Creates clean URL slugs for chapter navigation."""
    return "".join(ch.lower() if ch.isalnum() else "-" for ch in (title or "")).strip("-")


def generate_documentation_md(summary: str | None, chapters: List[Dict[str, str]]) -> str:
    """Combines overview and chapters into downloadable Markdown."""
    md = "# Overview\n\n"
    if summary:
        md += summary + "\n\n"
    else:
        md += "No overview summary available.\n\n"
    md += "## Chapters\n\n"
    for i, c in enumerate(chapters, start=1):
        md += f"### Chapter {i}: {c['title']}\n\n"
        md += c['content'] + "\n\n"
    return md


# ---------- Session Initialization ----------
if "current_page" not in st.session_state:
    st.session_state.current_page = "input_page"


# ---------- Sidebar Navigation ----------
st.sidebar.title("Codebase Genius")
if st.sidebar.button("Input Page"):
    st.session_state.current_page = "input_page"
if st.sidebar.button("Tutorial Page"):
    st.session_state.current_page = "tutorial_page"


# ---------- Input Page ----------
if st.session_state.current_page == "input_page":
    st.title("Codebase Genius")
    st.markdown("##### Convert a GitHub repository into an easy-to-read tutorial")
    st.caption("Enter a public GitHub repository URL to automatically generate its documentation and tutorial.")

    with st.form("repo_form"):
        repo_url = st.text_input("GitHub Repository URL*", placeholder="https://github.com/user/repo.git")
        submitted = st.form_submit_button("Generate Documentation")

    if submitted:
        if not repo_url:
            st.error("Please provide a GitHub Repository URL")
        else:
            with st.spinner("Initializing process..."):
                try:
                    progress_text = st.empty()
                    progress_text.text("Step 1: Cloning and mapping repository...")
                    payload = call_jac_supervisor(repo_url)
                    progress_text.text("Repository mapping completed.")
                    progress_text.text("Step 2: Code analysis started...")
                    progress_text.text("Code analysis completed.")
                    progress_text.text("Step 3: Generating documentation...")
                    chapters = normalize_chapters(payload["chapters"])
                    st.session_state["chapters"] = chapters
                    st.session_state["summary"] = payload.get("summary")
                    st.session_state["repo_url"] = repo_url
                    st.success("Tutorial successfully generated!")
                    st.session_state.current_page = "tutorial_page"
                except requests.HTTPError as e:
                    st.error(f"Backend error: {getattr(e.response, 'status_code', '??')} — {getattr(e.response, 'text', str(e))[:500]}")
                except Exception as e:
                    st.error(f"Failed to contact backend: {e}")


# ---------- Tutorial Display Page ----------
elif st.session_state.current_page == "tutorial_page":
    chapters: List[Dict[str, str]] = st.session_state.get("chapters", [])
    summary: str | None = st.session_state.get("summary")
    repo_url = st.session_state.get("repo_url")

    if not chapters:
        st.warning("No tutorial found. Please generate a tutorial first.")
        if st.button("← Go Back to Input Page"):
            st.session_state.current_page = "input_page"
    else:
        tutorial_md = generate_documentation_md(summary, chapters)

        # Sidebar navigation
        with st.sidebar:
            st.header("Chapters")
            options = ["Overview"] + [c["title"] for c in chapters]
            choice = st.radio("Go to Chapter", options, index=0)
            if choice == "Overview":
                st.markdown("### Overview")
            st.download_button("⬇Download Tutorial", tutorial_md, file_name="tutorial.md", mime="text/markdown")

        # Main content
        if choice == "Overview":
            st.header("Overview")
            st.markdown(f"**Repository:** {repo_url}")
            if summary:
                st.markdown("---")
                st.markdown(summary)
            st.markdown("---")
            st.markdown("### Chapters")
            for i, c in enumerate(chapters, start=1):
                st.markdown(f"**{i}. {c['title']}**")
        else:
            chapter = next((c for c in chapters if c["title"] == choice), None)
            if chapter:
                st.header(chapter["title"])
                st.markdown(chapter["content"])
            else:
                st.warning("Chapter not found.")

# """
# -----------------------------------------------------------
# LOGIC FLOW SUMMARY:
# 1. User enters GitHub repo URL.
# 2. Streamlit calls backend Supervisor walker (Jac HTTP API).
# 3. Backend clones repo, summarizes, analyzes, and generates docs.
# 4. Frontend shows progress steps and final Markdown tutorial.
# 5. User can navigate chapters or download the tutorial file.
# -----------------------------------------------------------
# """
