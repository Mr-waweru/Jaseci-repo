# --------------------------------------------------------
# Purpose: Implements the Supervisor walker and supporting node logic
# for the Codebase Genius backend. This handles cloning, analysis, and
# documentation generation from a GitHub repository.
# --------------------------------------------------------
# Node Responsibilities:
#  - RepoMapper: Clones the repo and summarizes its contents.
#  - CodeAnalyzer: Reads and processes files to extract abstractions
#    and relationships.
#  - DocGenie: Generates chapters, overview, and saves final markdown.
# --------------------------------------------------------

import from pathlib { Path }
import from git { Repo }
import from os { path }
import json;
import os;

# --- RepoMapper Node Implementation ---
impl RepoMapper.repo_clone(repo_url: str) {
    print("Step 1: Cloning repository (impl)...");
    try {
        # prefer existing self.repo_path (set by Supervisor.start), else build default
        to_path = getattr(self, "repo_path", "");
        if (not to_path or to_path == "") {
            repo_name = os.path.basename(repo_url).replace(".git", "");
            to_path = f"./outputs/{repo_name}";
            # persist for later stages
            setattr(self, "repo_path", to_path);
        }

        # ensure directory exists
        Path(to_path).mkdir(parents=True, exist_ok=True);
        print(f"DEBUG: cloning {repo_url} -> {to_path}");

        # GitPython requires destination path argument
        Repo.clone_from(repo_url, to_path);

        print("Repository cloned successfully!");
    }
    except Exception as e {
        print("Error cloning repository: " + str(e));
        raise e;
    }
}

impl RepoMapper.read_in_chunks(file_path: any, chunk_size: any = 150) {
    with open(file_path, 'r', encoding='utf-8') as f  {
        chunk = [];
        for (line_num, line) in enumerate(f, 1) {
            chunk.append(line);
            if ((line_num % chunk_size) == 0) {
                yield ''.join(chunk);
                chunk = [];
            }
        }
        if chunk {
            yield ''.join(chunk);
        }
    }
}

# --- CodeAnalyzer Node Implementation ---
impl CodeAnalyzer.read_files_from_list(file_paths: list[ str ]) -> dict {
    files_dict = {};
    total_files = len(file_paths);
    processed_files = 0;
    print("Step 2: Code analysis started...");
    for filepath in file_paths {
        relpath = os.path.basename(filepath).replace('.', '_');
        status ='processed';
        with open(filepath, 'r', encoding='utf-8-sig') as f {
            content = f.read();
        }
        files_dict[ relpath ] = [content];
        processed_files += 1;
        if (total_files > 0) {
            percentage = ((processed_files / total_files) * 100);
            rounded_percentage = int(percentage);
            print(f"Progress: {processed_files}/{total_files} ({rounded_percentage}%) {relpath} [{status}]");
        }
    }
    print("Code analysis completed.");
    print(f"\nFound {len(files_dict)} readable files:");
    for path in files_dict { print(f"  {path}"); }
    return files_dict;
}

# --- Supervisor Walker Implementation (impl) ---
impl Supervisor.start {
    print("🚀 Starting Supervisor workflow (impl.start)...");
    print(f"DEBUG: self.repo_url = {self.repo_url}");


    ExDocGenie_nodes = [root --> (`?DocGenie: saved_repo_url==self.repo_url)];
    if ExDocGenie_nodes {
        report{"overview":ExDocGenie_nodes[0].overview};
        report{"documentation":ExDocGenie_nodes[0].chapters};
        disengage;
    } else {
        here ++> RepoMapper();
        RepoMapper_nodes = [root --> RepoMapper];
        Repo = RepoMapper_nodes[-1];

        # --- Clone Repo Automatically ---
        import from pathlib { Path }
        repo_name = os.path.basename(self.repo_url).replace(".git", "");
        self.repo_path = f"./outputs/{repo_name}";
        Path(self.repo_path).mkdir(parents=True, exist_ok=True);

        # call repo_clone with single arg (impl uses self.repo_path internally)
        Repo.repo_clone(self.repo_url);

        # --- Summarize README ---
        file_directory = Path(self.repo_path + "/README.md");
        if file_directory.exists() {
            for (i, chunk_text) in enumerate(Repo.read_in_chunks(file_directory, 200), 1) {
                print("Summarizing README chunk...");
                response = get_summary(chunk_text, Repo.summary);
                Repo.summary = response;
            }
            print("Repository mapping completed.");
        } else {
            Repo.summary = "No README.md found in the repository.";
        }

        # --- Filter Meaningful Files ---
        print("Step 3: Filtering important project files...");
        # PASS A STRING path (not pathlib.Path) to LLM tool schema-friendly signature
        Repo.folder_structure = get_filtered_folder_structure(self.repo_path, Repo.summary);

        # --- Code Analysis Phase ---
        here ++> CodeAnalyzer();
        CodeAnalyzer_nodes = [root --> CodeAnalyzer];
        Code = CodeAnalyzer_nodes[-1];
        Code.code_base = Code.read_files_from_list(Repo.folder_structure);

        # --- Extract Project Abstractions ---
        print("Step 4: Extracting abstractions...");
        Code.abstractions = extract_abstractions(Code.code_base);

        # --- Identify Relationships ---
        print("Step 5: Identifying relationships...");
        Code.relationships = get_relationships(Code.abstractions);

        # --- Determine Chapter Order ---
        print("Step 6: Determining chapter order...");
        Code.chapter_order = chapter_ordering(Repo.summary, Code.abstractions, Code.relationships);

        # --- Documentation Generation ---
        here ++> DocGenie();
        DocGenie_nodes = [root --> DocGenie];
        Doc = DocGenie_nodes[-1];
        Doc.saved_repo_url = self.repo_url;

        print("Step 7: Drafting chapters...");
        Doc.drafted_chapters = chapter_drafting(Code.abstractions, Code.code_base);

        print("Step 8: Generating overview...");
        Doc.overview = generate_overview(Code.abstractions, Code.relationships);
        report{"overview":Doc.overview};

        print("Step 9: Generating docs...");
        Doc.chapters = generate_documentation(Doc.drafted_chapters);
        report{"documentation":Doc.chapters};

        # --- Save Documentation Locally ---
        print("Step 10: Saving docs locally...");
        output_dir = Path(f"./outputs/{repo_name}");
        if not output_dir.exists() {
            output_dir.mkdir(parents=True, exist_ok=True);
        }
        docs_path = output_dir / "docs.md";

        md_output = "# Overview\n\n" + (Doc.overview if Doc.overview else "") + "\n\n## Chapters\n\n";
        for (i, chapter) in enumerate(Doc.chapters, 1) {
            # chapter.title and chapter.content expected to exist on chapter objects
            chapter_title = chapter.title if getattr(chapter, "title", None) else (chapter.get("title") if hasattr(chapter, "get") else "Chapter");
            chapter_content = chapter.content if getattr(chapter, "content", None) else (chapter.get("content") if hasattr(chapter, "get") else "");
            md_output = md_output + "### Chapter " + str(i) + ": " + chapter_title + "\n\n" + chapter_content + "\n\n";
        }

        with open(docs_path, "w", encoding="utf-8") as f {
            f.write(md_output);
        }
        print(f"Documentation saved locally at: {docs_path}");
    }
}



# --------------------------------------------------------
# LOGIC FLOW SUMMARY
# 1. Supervisor starts → creates RepoMapper node → clones repository.
# 2. Summarizes README.md and filters meaningful source files.
# 3. Creates CodeAnalyzer node → reads all files and extracts abstractions.
# 4. Builds relationships and determines chapter order.
# 5. Creates DocGenie node → drafts chapters and overview.
# 6. Generates documentation Markdown and saves docs under ./outputs/<repo_name>/docs.md.
# 7. Reports overview and documentation back to frontend for display.
# --------------------------------------------------------
