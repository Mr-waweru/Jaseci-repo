"""
Streamlit frontend for Codebase Genius (resilient walker calls).

This file handles user input (GitHub repo URL), calls the Jac backend
Supervisor walker, normalizes the backend response into an "overview"
and "documentation" (list of chapters), and renders the results.

It includes defensive handling for multiple response shapes produced by
the Jac backend and provides a download button which names the file
`<repo_name>_docs.md` (with fallback `documentation.md`).
"""

import streamlit as st
import requests
from typing import List, Dict, Any
import os

BASE_BACKEND = "http://localhost:8000"
WALKER_ENDPOINT = f"{BASE_BACKEND}/walker/Supervisor"  # call without /start to avoid NodeAnchor errors

def call_jac_supervisor(repo_url: str) -> Dict[str, Any]:
    """Call the Jac backend and return parsed JSON (or {'raw': text})."""
    if repo_url and repo_url.startswith("github.com"):
        repo_url = "https://" + repo_url
    payload = {"repo_url": repo_url}
    try:
        r = requests.post(WALKER_ENDPOINT, json=payload, timeout=600)
        r.raise_for_status()
        try:
            return r.json()
        except ValueError:
            return {"raw": r.text}
    except requests.RequestException as e:
        raise RuntimeError(f"Error contacting Jac backend: {e}") from e

def _extract_from_reports(reports: list) -> Dict[str, Any]:
    overview = None
    tutorial = None

    for rep in reports:
        # If report is a dict and directly contains overview/tutorial
        if isinstance(rep, dict):
            if overview is None and rep.get("overview"):
                overview = rep.get("overview")
            if tutorial is None and rep.get("tutorial"):
                tutorial = rep.get("tutorial")

            # Some reports wrap tutorial inside 'context' or nested dicts
            for k, v in rep.items():
                if tutorial is None and isinstance(v, list):
                    # Heuristic: list of chapters (chapter objects often have 'title' or 'context' or 'id')
                    if v and (isinstance(v[0], dict) and ("title" in v[0] or "context" in v[0] or "id" in v[0])):
                        tutorial = v

        # If we've got both, stop early
        if overview is not None and tutorial is not None:
            break

    return {"overview": overview, "tutorial": tutorial}

def normalize_raw_response(resp: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize backend response into a dict with keys:
      - 'overview' : str | None
      - 'tutorial' : list | None
    """
    if not isinstance(resp, dict):
        return {"overview": None, "tutorial": None, "raw": str(resp)}

    # direct keys
    overview = resp.get("overview")
    tutorial = resp.get("tutorial")

    # if not present, inspect 'reports' array (Jaseci style)
    if (not overview and not tutorial) and resp.get("reports"):
        extracted = _extract_from_reports(resp.get("reports"))
        overview = overview or extracted.get("overview")
        tutorial = tutorial or extracted.get("tutorial")

    result = {"overview": overview, "tutorial": tutorial}
    if "raw" in resp:
        result["raw"] = resp["raw"]
    return result

def normalize_chapters(raw: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    Convert a variety of chapter representations to a list of {title, content}.
    Accepts strings, simple dicts, and dicts with nested 'context'.
    """
    norm = []
    if not raw:
        return norm
    for item in raw:
        if isinstance(item, str):
            norm.append({"title": "Chapter", "content": item})
            continue
        if isinstance(item, dict):
            # Many shapes: { "title":..., "content":... } OR { "context": { "title":..., "content":... } } OR { "id":..., "context":{...} }
            ctx = {}
            if "context" in item and isinstance(item["context"], dict):
                ctx = item["context"]
            # fallback include top-level fields
            title = ctx.get("title") or item.get("title") or item.get("name") or item.get("id") or "Untitled"
            content = ctx.get("content") or item.get("content") or item.get("body") or ""
            # if content is still a list/dict, stringify safely
            if isinstance(content, (list, dict)):
                try:
                    import json as _json
                    content = _json.dumps(content, indent=2)
                except Exception:
                    content = str(content)
            norm.append({"title": title, "content": content})
            continue
        # unknown type
        norm.append({"title": "Chapter", "content": str(item)})
    return norm

def generate_documentation_md(summary: str | None, chapters: List[Dict[str, str]]) -> str:
    md = "# Overview\n\n" + (summary or "No overview available.") + "\n\n## Chapters\n\n"
    for i, c in enumerate(chapters, start=1):
        md += f"### Chapter {i}: {c.get('title','Untitled')}\n\n{c.get('content','')}\n\n"
    return md

# ---------- Streamlit UI ----------
if "current_page" not in st.session_state:
    st.session_state.current_page = "input_page"

st.sidebar.title("Codebase Genius")
if st.sidebar.button("Input Page"):
    st.session_state.current_page = "input_page"
if st.sidebar.button("Documentation Page"):
    st.session_state.current_page = "documentation_page"

if st.session_state.current_page == "input_page":
    st.title("Codebase Genius")
    st.markdown("##### Convert a GitHub repository into an easy-to-read docs")
    with st.form("repo_form"):
        repo_url = st.text_input("GitHub Repository URL*", placeholder="https://github.com/user/repo")
        submitted = st.form_submit_button("Generate Documentation")

    if submitted:
        if not repo_url:
            st.error("Please provide a GitHub Repository URL")
        else:
            with st.spinner("Processing..."):
                try:
                    raw_resp = call_jac_supervisor(repo_url)
                    norm = normalize_raw_response(raw_resp)
                    overview = norm.get("overview")
                    raw_tutorial = norm.get("tutorial") or []

                    # normalize chapters (we'll now treat these as 'documentation chapters')
                    documentation_chapters = normalize_chapters(raw_tutorial)

                    # Defensive: if both overview and documentation are empty, show raw debug output
                    if (not overview or str(overview).strip() == "") and (not documentation_chapters or len(documentation_chapters) == 0):
                        st.error("No documentation generated. Backend response (raw):")
                        # show raw JSON or raw text for debugging
                        st.code(raw_resp if isinstance(raw_resp, str) else str(raw_resp)[:2000])
                    else:
                        # store as documentation pieces in session state
                        st.session_state.update({
                            "documentation_summary": overview,
                            "documentation_chapters": documentation_chapters,
                            "repo_url": repo_url
                        })
                        st.success("Documentation generated successfully!")
                        st.session_state.current_page = "documentation_page"
                except Exception as e:
                    st.error(f"Error: {e}")

elif st.session_state.current_page == "documentation_page":
    documentation_chapters = st.session_state.get("documentation_chapters", [])
    summary = st.session_state.get("documentation_summary")
    repo_url = st.session_state.get("repo_url")
    if not documentation_chapters:
        st.warning("No documentation found. Generate one first.")
        if st.button("← Go Back"):
            st.session_state.current_page = "input_page"
    else:
        docs_md = generate_documentation_md(summary, documentation_chapters)

        # derive repo_name for download filename
        repo_name = ""
        if repo_url:
            try:
                repo_name = os.path.basename(repo_url.rstrip("/")).replace(".git", "")
            except Exception:
                repo_name = "repository"

        with st.sidebar:
            st.header("Chapters")
            choice = st.radio("Go to Chapter", ["Overview"] + [c["title"] for c in documentation_chapters], index=0)
            # file name format requested: <repo_name>docs.md (e.g. UniStaydocs.md)
            filename = f"{repo_name}_docs.md" if repo_name else "documentation.md"
            st.download_button("⬇ Download Documentation", docs_md, file_name=filename, mime="text/markdown")

        if choice == "Overview":
            st.header("Overview")
            st.markdown(f"**Repository:** {repo_url}")
            if summary:
                st.markdown(summary)
        else:
            chapter = next((c for c in documentation_chapters if c["title"] == choice), None)
            if chapter:
                st.header(chapter["title"])
                st.markdown(chapter["content"])

# -----------------------------------------------------------
# LOGIC FLOW SUMMARY:
# 1. User inputs GitHub URL and submits form.
# 2. Frontend posts to Jac backend /walker/Supervisor.
# 3. Normalizes the backend response into `overview` and `documentation` (chapters).
# 4. If successful, stores summary + chapters in session_state and shows docs_page.
# 5. On docs_page, user can navigate chapters and download the docs as `<repo_name>_docs.md`.
# -----------------------------------------------------------