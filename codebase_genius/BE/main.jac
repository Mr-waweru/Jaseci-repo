# --------------------------------------------------------
# Purpose: Supervisor Interface
# --------------------------------------------------------

import from git { Repo }
import from pathlib { Path }
import from dotenv { load_dotenv }
import from byllm.llm { Model }
import os;
import from utils { get_summary,get_filtered_folder_structure,extract_abstractions,get_relationships,chapter_ordering,chapter_drafting,generate_tutorial, generate_overview }

node RepoMapper {
    has folder_structure: list[str]=[];
    has summary: str= "";

    def read_in_chunks(file_path: any, chunk_size: any = 150);
    def repo_clone(repo_url: str, repo_dir: str);
}

node CodeAnalyzer {
    has code_base: dict = {};
    has abstractions: list = [];
    has relationships: list = [];
    has chapter_order: list = [];

    def read_files_from_list(file_paths: list[ str ]) -> dict();
}

node DocGenie {
    has saved_repo_url: str= "";
    has drafted_chapters: list = [];
    has overview: str = "";
    has chapters: list = [];
    has diagrams: list = [];
}

walker Supervisor {
    has repo_url: str= "";
    has repo_path: str= "";

    obj __specs__{
        static has auth: bool = False;
    }
    can start with `root entry;
}