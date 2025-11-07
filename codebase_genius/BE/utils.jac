import from dotenv { load_dotenv }
import from byllm.llm { Model }
import os;

glob llm = Model(model_name="gemini/gemini-2.0-flash", verbose=False);

"""obtain this chunk of text and summary of get so far and give the response as the new summary of the chunk of text combined with the given summary so far, maximum 150 lines."""
def get_summary(text_chunk: str, summary: str) -> str by llm();


def get_all_file_paths(repo_path: str) -> list {
    all_files = [];
    if (repo_path.exists() and repo_path.is_dir() ) {
        for file_path in repo_path.rglob('*') { 
            if file_path.is_file() {
                all_files.append(str(file_path.resolve()));
            }
        }
    }
    return all_files;
}
"""Given a cloned GitHub repository path and a project summary, 
identify and filter out non-essential files. You can use get_all_file_paths function as a tool for getting all file paths as list from given repo_path. Also use summary for understanding the project context.
Return a list of only the meaningful source code files that are crucial for understanding the project's logic and abstractions. Exclude documentationumentation, configuration, test, and dependency files.""" 
def get_filtered_folder_structure(repo_path: str , summary: str ) -> list by llm(method="ReAct", tools=[get_all_file_paths]);


obj Absts {
    has name: str;
    has description: str;
    has related_files: list[];
}
"""Obtain all_codes and identify new abstractions atleast 5 or 6.
    All the Absts objects values output as a String."""
def extract_abstractions(all_codes: dict) -> list[Absts] by llm(method='Reason');


obj Rels {
    has from_abstraction: str;
    has to_abstraction: str;
    has label: str;
}
"""Obtain given project abstractions and identify key relationships between the abstractions for understanding best order of abstractions to explain. 
    Each relationship should show a from_abstraction, to_abstraction, and a brief label(A brief (a few words) description of the interaction)."""
def get_relationships(abstractions: list) -> list[Rels] by llm(method='Reason');


"""Obtain given the project summary, all abstractions, and their all relationships,
    Determine best order to explain this project in a tutorial.
    Output the ordered list of abstraction indices"""
def chapter_ordering(summary: str, all_abstractions: list, all_relationships: list) -> list[int] by llm(method="Reason");


obj Cformat {
    has heading: str;
    has highlevel_explanation_section: str;
    has key_concepts: str;
    has mermaid_diagram_section: str;
    has conclusion: str;
}
sem Cformat = "Cformat is a structured format for drafted chapters.";
sem Cformat.heading = "Clear heading of the chapter";
sem Cformat.highlevel_explanation_section = "High-level motivation explaining about the chapter content";
sem Cformat.key_concepts = "Key concepts covered in this chapter";
sem Cformat.mermaid_diagram_section = "Mermaid diagrams to illustrate high-level architecture as a String.";
sem Cformat.conclusion = "A concise conclusion summarizing the chapter content.";
"""Generate drafted chapters as a list of Cformat objects, for "String" types always use double quotes("..")"""
def chapter_drafting(abstractions_list: list, all_code_snippets: dict) -> list[Cformat] by llm();

"""Generate a beginner friendly comprehensive project overview in proper markdown format for proper rendering, including smooth transitions and consistent tone."""
def generate_overview(all_abstractions: list, all_relationships: list) -> str by llm();

obj Chapter {
    has title: str;
    has content: str;
}
sem Chapter = "complete Chapter for the tutorial.";
sem Chapter.title = "Clear and concise title of the chapter.";
sem Chapter.content = "Comprehensive content of the chapter.";
"""Generate a beginner friendly,readable, logically structured, and including mermaid diagrams visually aided complete chapters, including smooth transitions and consistent tone. Output *only* the Markdown content for this chapter, for "String" types always use double quotes("..").
Directly provide a super beginner-friendly Markdown output (DON'T need ```markdown``` tags). Use  (```mermaid``` format) for mermaid diagrams"""
def generate_documentation(all_drafted_chapters: list) -> list[Chapter] by llm();
