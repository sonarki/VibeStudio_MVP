"""Doc Node Map server.

Scans a documents folder and serves an auto-generated node map:
- GET /                → interactive graph view (self-contained HTML, no CDN)
- GET /api/nodemap     → graph as JSON ({nodes, edges, counts})

Usage:
    export DOCS_DIR=~/Documents   # optional; defaults shown below
    python server.py              # or: uvicorn server:app --port 8765

Truth note: local-only tool. It reads file names/sizes and (for .md/.txt)
file contents to find cross-links. Nothing leaves your machine.
"""

import os

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

from docmap.scanner import scan_folder
from docmap.viz import render_html

# Default scan target: $DOCS_DIR, else ~/Documents if it exists, else CWD.
_docs = os.environ.get("DOCS_DIR") or os.path.expanduser("~/Documents")
DEFAULT_DIR = _docs if os.path.isdir(os.path.expanduser(_docs)) else os.getcwd()

app = FastAPI(title="VibeStudio Doc Node Map", version="0.1.0")


def _scan_or_400(path: str, max_nodes: int) -> dict:
    try:
        return scan_folder(path, max_nodes=max_nodes).to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/nodemap")
def api_nodemap(
    path: str = Query(default=DEFAULT_DIR, description="Folder to scan"),
    max_nodes: int = Query(default=800, ge=10, le=5000),
):
    """Scan `path` and return the node map as JSON."""
    return _scan_or_400(path, max_nodes)


@app.get("/", response_class=HTMLResponse)
def index(
    path: str = Query(default=DEFAULT_DIR, description="Folder to scan"),
    max_nodes: int = Query(default=800, ge=10, le=5000),
):
    """Scan `path` and render the interactive node map."""
    return render_html(_scan_or_400(path, max_nodes))


if __name__ == "__main__":
    port = int(os.environ.get("DOCMAP_PORT", "8765"))
    print(f"Doc Node Map → http://localhost:{port}/  (scanning: {DEFAULT_DIR})")
    uvicorn.run(app, host="127.0.0.1", port=port)
