import from dotenv { load_dotenv }
import from byllm.llm { Model }
import from pathlib { Path }
import os;

glob llm = Model(model_name="gemini/gemini-2.0-flash", verbose=False);

"""obtain this chunk of text and summary of get so far and give the response as the new summary of the chunk of text combined with the given summary so far, maximum 150 lines."""
def get_summary(text_chunk: str, summary: str) -> str by llm();

"""Return all file paths under repo_path (repo_path passed as a string)."""
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
identify and filter out non-essential files. Return only meaningful source code files."""
def get_filtered_folder_structure(repo_path: str, summary: str ) -> list[str] by llm(method="ReAct", tools=[get_all_file_paths]);

obj Absts {
    has name: str;
    has description: str;
    has related_files: list[str] = [];
}

"""Obtain all_codes and identify new abstractions at least 5 or 6."""
def extract_abstractions(all_codes: dict) -> list[Absts] by llm(method='Reason');

obj Rels {
    has from_abstraction: str;
    has to_abstraction: str;
    has label: str;
}

"""Identify key relationships between the abstractions."""
def get_relationships(abstractions: list[Absts]) -> list[Rels] by llm(method='Reason');

"""Determine best order to explain this project in a tutorial."""
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

sem Chapter = "Complete chapter for the tutorial.";

"""Generate beginner-friendly Markdown chapters including mermaid diagrams."""
def generate_documentation(all_drafted_chapters: list[Cformat]) -> list[Chapter] by llm();
