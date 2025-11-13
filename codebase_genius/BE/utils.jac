import from dotenv { load_dotenv }
import from byllm.llm { Model }
import from pathlib { Path }
import os;
import time;

glob llm = Model(model_name="gemini/gemini-2.0-flash", verbose=False);

"""obtain this chunk of text and summary so far and return the updated summary.
This tool is intended to be used by the Supervisor to iteratively summarize
large README files in chunks.
"""
def get_summary(text_chunk: str, summary: str, max_retries: int = 3) -> str {
    for attempt in range(max_retries) {
        try {
            return get_summary_impl(text_chunk, summary);
        } except Exception as e {
            if "503" in str(e) or "overloaded" in str(e).lower() {
                if attempt < max_retries - 1 {
                    wait_time = (2 ** attempt);  # Exponential backoff: 1s, 2s, 4s
                    print(f"API overloaded, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})");
                    time.sleep(wait_time);
                } else {
                    print("Max retries reached. API still unavailable.");
                    raise e;
                }
            } else {
                raise e;
            }
        }
    }
}

def get_summary_impl(text_chunk: str, summary: str) -> str by llm();

"""Return all file paths under repo_path (repo_path passed as a string).
This helper is used as a supporting tool for the LLM-based file filtering
function which expects a simple JSON-serializable signature.
"""
def get_all_file_paths(repo_path: str) -> list[str] {
    all_files = [];
    try {
        repo_p = Path(repo_path);
        if (repo_p.exists() and repo_p.is_dir() ) {
            for file_path in repo_p.rglob('*') {
                if file_path.is_file() {
                    all_files.append(str(file_path.resolve()));
                }
            }
        }
    } except Exception as e {
        print(f"[get_all_file_paths] error: {e}");
    }
    return all_files;
}


"""Given a cloned GitHub repository path (string) and a project summary,
identify and filter out non-essential files. Return only meaningful source code files.
This is a high-level LLM tool that uses `get_all_file_paths` as a tool to get
candidate files, and then the LLM should return a filtered list of file paths.
"""
def get_filtered_folder_structure(repo_path: str, summary: str ) -> list[str] by llm(method="ReAct", tools=[get_all_file_paths]);

obj Absts {
    has name: str;
    has description: str;
    has related_files: list[str] = [];
}


"""Obtain all_codes and identify new abstractions (aim for 5-8 items).
The returned list is a list of `Absts` objects describing key concepts/abstractions
in the codebase and which files are related.
"""
def extract_abstractions(all_codes: dict) -> list[Absts] by llm(method='Reason');

obj Rels {
    has from_abstraction: str;
    has to_abstraction: str;
    has label: str;
}


"""Identify key relationships between the abstractions."""
def get_relationships(abstractions: list[Absts]) -> list[Rels] by llm(method='Reason');


"""Determine best order to explain this project in a docs."""
def chapter_ordering(summary: str, all_abstractions: list[Absts], all_relationships: list[Rels]) -> list[int] by llm(method="Reason");

obj Cformat {
    has heading: str;
    has highlevel_explanation_section: str;
    has key_concepts: str;
    has mermaid_diagram_section: str;
    has conclusion: str;
}

sem Cformat = "Structured format for drafted chapters.";


"""Generate drafted chapters as a list of Cformat objects."""
def chapter_drafting(abstractions_list: list[Absts], all_code_snippets: dict) -> list[Cformat] by llm();

"""Generate a beginner friendly comprehensive project overview in proper markdown format."""
def generate_overview(all_abstractions: list[Absts], all_relationships: list[Rels]) -> str by llm();

obj Chapter {
    has title: str;
    has content: str;
}

sem Chapter = "Complete chapter for the documentation.";

"""Generate beginner-friendly Markdown chapters including mermaid diagrams."""
def generate_documentation(all_drafted_chapters: list[Cformat]) -> list[Chapter] by llm();


# -------------------------
# LOGIC FLOW SUMMARY
# 1. LLM instance byllm created for use by tool functions.
# 2. get_all_file_paths enumerates repo files (helper used by LLM tool schema).
# 3. LLM tools:
#    - get_summary: iterative README summarization
#    - get_filtered_folder_structure: filter meaningful files using get_all_file_paths
#    - extract_abstractions, get_relationships, chapter_ordering, chapter_drafting,
#      generate_overview, generate_documentation: high-level LLM-driven steps
# 4. The Supervisor orchestrates calling these tools; helper functions keep signatures
#    LLM-schema friendly (primitive types like string lists).
# -------------------------