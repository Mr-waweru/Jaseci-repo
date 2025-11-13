"""
Unified API combining Jac backend and CCG query endpoints.
Endpoints:
- POST /walker/Supervisor - Main documentation generation (Jac)
- GET /ccg/graph?repo_name=... - Get full CCG graph
- GET /ccg/relationships?repo_name=...&function=...&direction=...&depth=... - Query function relationships
- DELETE /cache/{repo_name} - Clear cached data for a repo
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import json
from pathlib import Path
import shutil
import uvicorn

# Import Jac Cloud API setup
try:
    import jac_cloud.jaseci as jac_api
    JAC_AVAILABLE = True
except ImportError:
    JAC_AVAILABLE = False
    print("Warning: jac_cloud not available")

app = FastAPI(title="Codebase Genius Unified API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============= JAC BACKEND ENDPOINTS =============
# This file just adds the CCG endpoints to the same server


# ============= CCG QUERY ENDPOINTS =============

@app.get("/ccg/graph")
async def get_ccg_graph(repo_name: str = Query(..., description="Repository name in outputs/")):
    """Get full CCG graph (nodes + edges) for a repository."""
    ccg_path = Path(f"./outputs/{repo_name}/ccg.json")
    
    if not ccg_path.exists():
        raise HTTPException(
            status_code=404, 
            detail=f"CCG not found for repo '{repo_name}'. Generate documentation first."
        )
    
    try:
        ccg_data = json.loads(ccg_path.read_text(encoding="utf-8"))
        return {
            "repo_name": repo_name,
            "nodes_count": len(ccg_data.get("nodes", [])),
            "edges_count": len(ccg_data.get("edges", [])),
            "ccg": ccg_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading CCG: {str(e)}")


@app.get("/ccg/relationships")
async def query_relationships(
    repo_name: str = Query(..., description="Repository name"),
    function: str = Query(..., description="Function to query (e.g., 'train_model' or 'module.py:train_model')"),
    direction: str = Query("both", description="Query direction: 'callers', 'callees', or 'both'"),
    depth: int = Query(1, ge=1, le=10, description="Traversal depth (1-10)")
):
    """
    Query function call relationships.
    
    Examples:
    - Which functions call train_model? 
      GET /ccg/relationships?repo_name=MyRepo&function=train_model&direction=callers&depth=1
      
    - What does train_model call?
      GET /ccg/relationships?repo_name=MyRepo&function=train_model&direction=callees&depth=1
      
    - Full call graph around train_model?
      GET /ccg/relationships?repo_name=MyRepo&function=train_model&direction=both&depth=2
    """
    ccg_path = Path(f"./outputs/{repo_name}/ccg.json")
    
    if not ccg_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"CCG not found for repo '{repo_name}'. Generate documentation first."
        )
    
    try:
        ccg = json.loads(ccg_path.read_text(encoding="utf-8"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading CCG: {str(e)}")
    
    # Build lookup maps
    nodes = ccg.get("nodes", [])
    edges = ccg.get("edges", [])
    
    node_map = {n["id"]: n for n in nodes}
    
    # Find matching nodes for the query function
    # Support exact match, suffix match, and bare name match
    matches = []
    function_lower = function.lower()
    
    for node_id in node_map.keys():
        node_id_lower = node_id.lower()
        # Exact match
        if node_id_lower == function_lower:
            matches.append(node_id)
            continue
        # Suffix match (e.g., "train_model" matches "module.py:train_model")
        if node_id_lower.endswith(f":{function_lower}") or node_id_lower.endswith(f".{function_lower}"):
            matches.append(node_id)
            continue
        # Bare name match
        bare_name = node_id.split(":")[-1].split(".")[-1].lower()
        if bare_name == function_lower:
            matches.append(node_id)
    
    if not matches:
        # Provide helpful candidates
        all_functions = sorted([
            n["id"] for n in nodes if n.get("type") == "function"
        ])[:50]
        raise HTTPException(
            status_code=404,
            detail={
                "error": f"Function '{function}' not found in CCG",
                "suggestion": "Try one of these function names",
                "candidates": all_functions
            }
        )
    
    # Build adjacency maps
    callers_map = {}  # function -> list of functions that call it
    callees_map = {}  # function -> list of functions it calls
    
    for edge in edges:
        src = edge.get("from")
        dst = edge.get("to")
        
        if not src or not dst:
            continue
        
        # Build callees map (forward direction)
        if src not in callees_map:
            callees_map[src] = []
        callees_map[src].append(dst)
        
        # Build callers map (backward direction)
        if dst not in callers_map:
            callers_map[dst] = []
        callers_map[dst].append(src)
    
    # Traverse graph
    def traverse_graph(start_node, forward=True, max_depth=1):
        """Traverse graph from start_node up to max_depth."""
        results = {}
        frontier = {start_node}
        visited = set()
        
        for d in range(max_depth):
            next_frontier = set()
            for node in frontier:
                if node in visited:
                    continue
                visited.add(node)
                
                # Get neighbors based on direction
                neighbors = []
                if forward:
                    neighbors = callees_map.get(node, [])
                else:
                    neighbors = callers_map.get(node, [])
                
                for neighbor in neighbors:
                    # Store with metadata
                    if neighbor not in results:
                        neighbor_info = node_map.get(neighbor, {})
                        results[neighbor] = {
                            "id": neighbor,
                            "name": neighbor_info.get("name", neighbor),
                            "type": neighbor_info.get("type", "unknown"),
                            "module": neighbor_info.get("module", "unknown"),
                            "depth": d + 1
                        }
                    next_frontier.add(neighbor)
            
            frontier = next_frontier
        
        return list(results.values())
    
    # Execute query based on direction
    result = {
        "repo_name": repo_name,
        "query": {
            "function": function,
            "direction": direction,
            "depth": depth
        },
        "matches": [
            {
                "id": m,
                "name": node_map[m].get("name", m),
                "type": node_map[m].get("type", "unknown"),
                "module": node_map[m].get("module", "unknown")
            }
            for m in matches
        ]
    }
    
    if direction in ("both", "callees"):
        result["callees"] = {}
        for match in matches:
            result["callees"][match] = traverse_graph(match, forward=True, max_depth=depth)
    
    if direction in ("both", "callers"):
        result["callers"] = {}
        for match in matches:
            result["callers"][match] = traverse_graph(match, forward=False, max_depth=depth)
    
    return result


@app.delete("/cache/{repo_name}")
async def clear_cache(repo_name: str):
    """Clear all cached data for a repository."""
    output_dir = Path(f"./outputs/{repo_name}")
    
    if not output_dir.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Repository '{repo_name}' not found in outputs"
        )
    
    try:
        # Remove all files and subdirectories
        for item in output_dir.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
        
        # Remove the directory itself
        output_dir.rmdir()
        
        return {
            "success": True,
            "message": f"Cache cleared for repository '{repo_name}'",
            "removed": str(output_dir)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing cache: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Codebase Genius Unified API",
        "jac_available": JAC_AVAILABLE
    }


# Instructions for mounting this with Jac
"""
To run this unified API with your Jac backend:

1. Make sure this file is in your BE/ directory
2. Run: jac serve main.jac --host 0.0.0.0 --port 8000

The Jac serve command will automatically mount additional FastAPI routes
from this module.
"""

if __name__ == "__main__":
    print("⚠️  Running in standalone mode")
    print("    For full functionality, run with: jac serve main.jac")
    print("    This will integrate Jac walker endpoints + CCG queries")
    uvicorn.run(app, host="0.0.0.0", port=9000)