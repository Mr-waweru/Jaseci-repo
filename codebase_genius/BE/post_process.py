# post_process.py
import os
import sys
import json
import shutil
import time
from pathlib import Path
from ccg_builder import build_ccg_from_repo

ALLOWED_FILES = {"docs.md", "ccg.json", "cached_docs.json"}


def atomic_write(path: Path, data: str):
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        f.write(data)
    tmp.replace(path)


def write_json_atomic(path: Path, obj):
    atomic_write(path, json.dumps(obj, indent=2))


def process_repo(repo_path: str):
    repo_path = Path(repo_path)
    if not repo_path.exists():
        raise FileNotFoundError(f"Repo path not found: {repo_path}")

    repo_name = repo_path.name
    print(f"[post_process] Processing: {repo_name} @ {repo_path}")

    # --- docs.md existence check ---
    docs_path = repo_path / "docs.md"
    if not docs_path.exists():
        print("No docs.md found. Nothing to cache or save. Exiting.")
        return {"ok": False, "reason": "no_docs"}

    docs_text = docs_path.read_text(encoding="utf-8")

    # --- write cached_docs.json ---
    cached = {
        "repo_name": repo_name,
        "cached_at": int(time.time()),
        "docs_preview": docs_text[:20000],
        "docs_len": len(docs_text),
    }
    write_json_atomic(repo_path / "cached_docs.json", cached)
    print("Wrote cached_docs.json")

    # --- build CCG ---
    try:
        ccg = build_ccg_from_repo(str(repo_path))
        write_json_atomic(repo_path / "ccg.json", ccg)
        print("Wrote ccg.json")
    except Exception as e:
        print(f"Error building CCG: {e}")
        # still continue to cleanup

    # --- cleanup: remove anything that isn't allowed ---
    for p in repo_path.iterdir():
        if p.name in ALLOWED_FILES:
            continue
        try:
            if p.is_dir():
                shutil.rmtree(p)
            else:
                p.unlink()
            print(f"Removed {p}")
        except Exception as e:
            print(f"Failed to remove {p}: {e}")

    print("Post-processing completed — outputs preserved: docs.md, ccg.json, cached_docs.json")
    return {"ok": True}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python post_process.py /path/to/outputs/<repo_name>")
        sys.exit(2)
    repo_dir = sys.argv[1]
    r = process_repo(repo_dir)
    print(r)