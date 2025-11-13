"""
Streamlit frontend for Codebase Genius with CCG query interface.

Features:
- Generate documentation from GitHub repos
- Query function relationships using natural language
- Visualize call graphs
- Download documentation
"""

import streamlit as st
import requests
from typing import List, Dict, Any
import os

BASE_BACKEND = "http://localhost:8000"
WALKER_ENDPOINT = f"{BASE_BACKEND}/walker/Supervisor"
CCG_ENDPOINT = f"{BASE_BACKEND}/ccg"

def call_jac_supervisor(repo_url: str) -> Dict[str, Any]:
    """Call the Jac backend and return parsed JSON."""
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


def query_ccg_relationships(repo_name: str, function: str, direction: str = "both", depth: int = 1):
    """Query function relationships from CCG."""
    try:
        params = {
            "repo_name": repo_name,
            "function": function,
            "direction": direction,
            "depth": depth
        }
        r = requests.get(f"{CCG_ENDPOINT}/relationships", params=params, timeout=30)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        raise RuntimeError(f"Error querying CCG: {e}") from e


def _extract_from_reports(reports: list) -> Dict[str, Any]:
    overview = None
    tutorial = None

    for rep in reports:
        if isinstance(rep, dict):
            if overview is None and rep.get("overview"):
                overview = rep.get("overview")
            if tutorial is None and rep.get("tutorial"):
                tutorial = rep.get("tutorial")

            for k, v in rep.items():
                if tutorial is None and isinstance(v, list):
                    if v and (isinstance(v[0], dict) and ("title" in v[0] or "context" in v[0] or "id" in v[0])):
                        tutorial = v

        if overview is not None and tutorial is not None:
            break

    return {"overview": overview, "tutorial": tutorial}


def normalize_raw_response(resp: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize backend response."""
    if not isinstance(resp, dict):
        return {"overview": None, "tutorial": None, "raw": str(resp)}

    overview = resp.get("overview")
    tutorial = resp.get("tutorial")

    if (not overview and not tutorial) and resp.get("reports"):
        extracted = _extract_from_reports(resp.get("reports"))
        overview = overview or extracted.get("overview")
        tutorial = tutorial or extracted.get("tutorial")

    result = {"overview": overview, "tutorial": tutorial}
    if "raw" in resp:
        result["raw"] = resp["raw"]
    return result


def normalize_chapters(raw: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Convert various chapter representations to {title, content}."""
    norm = []
    if not raw:
        return norm
    for item in raw:
        if isinstance(item, str):
            norm.append({"title": "Chapter", "content": item})
            continue
        if isinstance(item, dict):
            ctx = {}
            if "context" in item and isinstance(item["context"], dict):
                ctx = item["context"]
            title = ctx.get("title") or item.get("title") or item.get("name") or item.get("id") or "Untitled"
            content = ctx.get("content") or item.get("content") or item.get("body") or ""
            if isinstance(content, (list, dict)):
                try:
                    import json as _json
                    content = _json.dumps(content, indent=2)
                except Exception:
                    content = str(content)
            norm.append({"title": title, "content": content})
            continue
        norm.append({"title": "Chapter", "content": str(item)})
    return norm


def generate_documentation_md(summary: str | None, chapters: List[Dict[str, str]]) -> str:
    md = "# Overview\n\n" + (summary or "No overview available.") + "\n\n## Chapters\n\n"
    for i, c in enumerate(chapters, start=1):
        md += f"### Chapter {i}: {c.get('title','Untitled')}\n\n{c.get('content','')}\n\n"
    return md


def render_ccg_query_interface(repo_name: str):
    """Render CCG query interface."""
    st.header("🔍 Query Code Relationships")
    
    st.markdown("""
    Ask questions about your codebase:
    - Which functions call `function_name`?
    - What does `function_name` call?
    - Show me the call graph around `function_name`
    """)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        query_text = st.text_input(
            "Ask a question",
            placeholder="Which functions call train_model?",
            key="ccg_query"
        )
    
    with col2:
        depth = st.selectbox("Depth", [1, 2, 3], index=0, key="ccg_depth")
    
    if st.button("🔎 Search", key="ccg_search"):
        if not query_text:
            st.warning("Please enter a question")
            return
        
        # Parse natural language query
        query_lower = query_text.lower()
        
        # Extract function name
        function_name = None
        direction = "both"
        
        # Pattern matching for common questions
        import re
        
        # "Which functions call X" or "Who calls X"
        if "call" in query_lower:
            match = re.search(r"call[s]?\s+([a-zA-Z0-9_\.]+)", query_lower)
            if match:
                function_name = match.group(1)
                if "which" in query_lower or "who" in query_lower or "what" in query_lower:
                    direction = "callers"
        
        # "What does X call"
        if "does" in query_lower and "call" in query_lower:
            match = re.search(r"does\s+([a-zA-Z0-9_\.]+)\s+call", query_lower)
            if match:
                function_name = match.group(1)
                direction = "callees"
        
        # "callers of X" or "callees of X"
        if "callers of" in query_lower:
            match = re.search(r"callers\s+of\s+([a-zA-Z0-9_\.]+)", query_lower)
            if match:
                function_name = match.group(1)
                direction = "callers"
        
        if "callees of" in query_lower:
            match = re.search(r"callees\s+of\s+([a-zA-Z0-9_\.]+)", query_lower)
            if match:
                function_name = match.group(1)
                direction = "callees"
        
        # Fallback: assume last word is function name
        if not function_name:
            words = query_lower.split()
            if words:
                function_name = words[-1].strip("?.,!")
        
        if not function_name:
            st.error("Could not extract function name from query")
            return
        
        # Execute query
        with st.spinner(f"Searching for '{function_name}'..."):
            try:
                result = query_ccg_relationships(repo_name, function_name, direction, depth)
                
                # Display results
                st.success(f"Found matches for '{function_name}'")
                
                # Show matched functions
                if result.get("matches"):
                    with st.expander("📍 Matched Functions", expanded=True):
                        for match in result["matches"]:
                            st.code(f"{match['id']}\nType: {match['type']}\nModule: {match['module']}")
                
                # Show callers
                if result.get("callers"):
                    st.subheader("⬆️ Functions that call this")
                    for func_id, callers in result["callers"].items():
                        if callers:
                            with st.expander(f"Callers of {func_id}"):
                                for caller in callers:
                                    st.markdown(f"""
                                    - **{caller['name']}** (`{caller['id']}`)
                                      - Type: {caller['type']}
                                      - Module: {caller['module']}
                                      - Depth: {caller['depth']}
                                    """)
                        else:
                            st.info(f"No callers found for {func_id}")
                
                # Show callees
                if result.get("callees"):
                    st.subheader("⬇️ Functions this calls")
                    for func_id, callees in result["callees"].items():
                        if callees:
                            with st.expander(f"Callees of {func_id}"):
                                for callee in callees:
                                    st.markdown(f"""
                                    - **{callee['name']}** (`{callee['id']}`)
                                      - Type: {callee['type']}
                                      - Module: {callee['module']}
                                      - Depth: {callee['depth']}
                                    """)
                        else:
                            st.info(f"No callees found for {func_id}")
                
            except Exception as e:
                error_msg = str(e)
                if "404" in error_msg:
                    st.error("Function not found in the codebase")
                    # Try to show suggestions
                    try:
                        import json
                        error_data = json.loads(error_msg.split("detail=")[1] if "detail=" in error_msg else "{}")
                        if isinstance(error_data, dict) and "candidates" in error_data:
                            with st.expander("💡 Suggestions"):
                                st.write("Try one of these functions:")
                                for candidate in error_data["candidates"][:20]:
                                    st.code(candidate)
                    except:
                        pass
                else:
                    st.error(f"Query failed: {e}")


# ---------- Streamlit UI ----------
if "current_page" not in st.session_state:
    st.session_state.current_page = "input_page"

st.sidebar.title("Codebase Genius")
if st.sidebar.button("🏠 Generate Docs"):
    st.session_state.current_page = "input_page"
if st.sidebar.button("📚 View Documentation"):
    st.session_state.current_page = "documentation_page"
if st.sidebar.button("🔍 Query Relationships"):
    st.session_state.current_page = "query_page"

if st.session_state.current_page == "input_page":
    st.title("Codebase Genius")
    st.markdown("##### Convert a GitHub repository into easy-to-read documentation")
    
    with st.form("repo_form"):
        repo_url = st.text_input("GitHub Repository URL*", placeholder="https://github.com/user/repo")
        submitted = st.form_submit_button("Generate Documentation")

    if submitted:
        if not repo_url:
            st.error("Please provide a GitHub Repository URL")
        else:
            with st.spinner("Processing... This may take a few minutes"):
                try:
                    raw_resp = call_jac_supervisor(repo_url)
                    norm = normalize_raw_response(raw_resp)
                    overview = norm.get("overview")
                    raw_tutorial = norm.get("tutorial") or []

                    documentation_chapters = normalize_chapters(raw_tutorial)

                    if (not overview or str(overview).strip() == "") and (not documentation_chapters or len(documentation_chapters) == 0):
                        st.error("No documentation generated. Backend response (raw):")
                        st.code(raw_resp if isinstance(raw_resp, str) else str(raw_resp)[:2000])
                    else:
                        # Extract repo name
                        repo_name = os.path.basename(repo_url.rstrip("/")).replace(".git", "")
                        
                        st.session_state.update({
                            "documentation_summary": overview,
                            "documentation_chapters": documentation_chapters,
                            "repo_url": repo_url,
                            "repo_name": repo_name
                        })
                        st.success("✅ Documentation generated successfully!")
                        st.session_state.current_page = "documentation_page"
                        st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

elif st.session_state.current_page == "query_page":
    repo_name = st.session_state.get("repo_name")
    if not repo_name:
        st.warning("⚠️ Please generate documentation first")
        if st.button("← Go to Input Page"):
            st.session_state.current_page = "input_page"
            st.rerun()
    else:
        render_ccg_query_interface(repo_name)

elif st.session_state.current_page == "documentation_page":
    documentation_chapters = st.session_state.get("documentation_chapters", [])
    summary = st.session_state.get("documentation_summary")
    repo_url = st.session_state.get("repo_url")
    repo_name = st.session_state.get("repo_name", "")
    
    if not documentation_chapters:
        st.warning("No documentation found. Generate one first.")
        if st.button("← Go Back"):
            st.session_state.current_page = "input_page"
            st.rerun()
    else:
        docs_md = generate_documentation_md(summary, documentation_chapters)

        with st.sidebar:
            st.header("Chapters")
            choice = st.radio("Go to Chapter", ["Overview"] + [c["title"] for c in documentation_chapters], index=0)
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