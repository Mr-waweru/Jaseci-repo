"""
Goal:
 - Extract functions, classes, and call relationships
 - Produce a graph: nodes (functions/methods) and edges (caller -> callee)
 - Export graph as JSON-serializable dict
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple

# Try to import tree_sitter optionally
try:
    from tree_sitter import Language, Parser
    TREE_SITTER_AVAILABLE = True
except Exception:
    TREE_SITTER_AVAILABLE = False

import ast


def parse_python(content: str, module_name: str):
    """Return nodes and edges for a python source using ast."""
    nodes = []
    edges = []

    class FuncVisitor(ast.NodeVisitor):
        def __init__(self):
            self.current_fn = None
            self.current_class = None

        def visit_ClassDef(self, node):
            cls_name = f"{module_name}:{node.name}"
            nodes.append({"id": cls_name, "type": "class", "name": node.name, "module": module_name})
            prev_class = self.current_class
            self.current_class = node.name
            self.generic_visit(node)
            self.current_class = prev_class

        def visit_FunctionDef(self, node):
            qual = node.name
            if self.current_class:
                nid = f"{module_name}:{self.current_class}.{node.name}"
            else:
                nid = f"{module_name}:{node.name}"
            nodes.append({"id": nid, "type": "function", "name": node.name, "module": module_name, "lineno": node.lineno})
            prev_fn = self.current_fn
            self.current_fn = nid
            self.generic_visit(node)
            self.current_fn = prev_fn

        def visit_Call(self, node):
            # get called name best-effort
            func = node.func
            called = None
            if isinstance(func, ast.Name):
                called = func.id
            elif isinstance(func, ast.Attribute):
                # extract attr chain like obj.method or Class.method
                parts = []
                cur = func
                while isinstance(cur, ast.Attribute):
                    parts.append(cur.attr)
                    cur = cur.value
                if isinstance(cur, ast.Name):
                    parts.append(cur.id)
                full = list(reversed(parts))
                called = ".".join(full)
            if called and self.current_fn:
                edges.append({"from": self.current_fn, "to": called, "label": "calls"})
            self.generic_visit(node)

    try:
        tree = ast.parse(content)
    except Exception:
        return {"nodes": nodes, "edges": edges}

    v = FuncVisitor()
    v.visit(tree)

    # post-process edges: normalize "to" to possible qualified ids when available
    # We keep raw 'to' names (like "train_model" or "models.train") for lookup.

    return {"nodes": nodes, "edges": edges}


# Simple regex-based extraction for other languages
FUNC_DEF_RE = re.compile(r"\b(def|function|fn)\s+([A-Za-z0-9_\.]+)\b")
CALL_RE = re.compile(r"([A-Za-z0-9_\.]+)\s*\(")
CLASS_DEF_RE = re.compile(r"\b(class|struct)\s+([A-Za-z0-9_\.]+)\b")


def parse_generic(content: str, module_name: str):
    nodes = []
    edges = []
    # find functions
    for m in FUNC_DEF_RE.finditer(content):
        name = m.group(2)
        nodes.append({"id": f"{module_name}:{name}", "type": "function", "name": name, "module": module_name})
    for m in CLASS_DEF_RE.finditer(content):
        name = m.group(2)
        nodes.append({"id": f"{module_name}:{name}", "type": "class", "name": name, "module": module_name})
    # primitive calls scan
    for m in CALL_RE.finditer(content):
        called = m.group(1)
        # Associate to nearest function by searching backward lines
        # best-effort: take the first function found in the file (coarse)
        if nodes:
            edges.append({"from": nodes[0]["id"], "to": called, "label": "calls"})
    return {"nodes": nodes, "edges": edges}


def build_ccg_from_repo(repo_path: str) -> Dict:
    """Walk repo files, parse them, and build a consolidated CCG.
    The returned structure is:
    {
        "nodes": [{id, type, name, module, lineno?}, ...],
        "edges": [{from, to, label}, ...]
    }
    """
    repo_path = Path(repo_path)
    nodes = []
    edges = []
    seen_nodes = set()

    for p in repo_path.rglob("*.*"):
        if p.name in {"docs.md", "ccg.json", "cached_docs.json"}:
            continue
        ext = p.suffix.lower()
        try:
            content = p.read_text(encoding="utf-8")
        except Exception:
            continue
        module_name = str(p.relative_to(repo_path))
        parsed = None
        if ext == ".py":
            parsed = parse_python(content, module_name)
        else:
            # Try tree-sitter if available for supported languages
            if TREE_SITTER_AVAILABLE:
                # NOTE: For a production setup, pre-build languages with tree-sitter CLI
                # and load them here (Language.build_library + Language(...)).
                # This implementation keeps tree-sitter optional due to local build complexity.
                parsed = parse_generic(content, module_name)
            else:
                parsed = parse_generic(content, module_name)

        for n in parsed.get("nodes", []):
            nid = n.get("id")
            if nid not in seen_nodes:
                nodes.append(n)
                seen_nodes.add(nid)
        for e in parsed.get("edges", []):
            edges.append(e)

    ccg = {"nodes": nodes, "edges": edges}
    return ccg
