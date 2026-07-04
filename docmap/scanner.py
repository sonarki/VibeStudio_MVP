"""Scan a documents folder and build a node map (nodes + edges).

Pure local logic: no network, no external services.
- Nodes: folders and document files (by extension).
- Edges: "contains" (folder -> child) and "links_to" (markdown/plain-text
  relative links between documents in the same tree).
"""

import os
import re
from dataclasses import dataclass, field

# Document types we surface as nodes. Everything else is counted but skipped.
DOC_EXTS = {
    ".md", ".txt", ".rst", ".pdf", ".doc", ".docx", ".rtf", ".odt",
    ".hwp", ".hwpx", ".ipynb", ".csv", ".tsv", ".xlsx", ".pptx",
}

# Folders never worth walking into.
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".idea", ".vscode"}

# Only these are cheap/safe to open for cross-link extraction.
TEXT_EXTS = {".md", ".txt", ".rst"}
MAX_TEXT_BYTES = 512 * 1024  # don't read huge files

# [label](target) — ignore anchors/queries; also bare relative links in <...>
_MD_LINK_RE = re.compile(r"\[[^\]]*\]\(\s*([^)#?\s]+)")


@dataclass
class NodeMap:
    root: str
    nodes: list = field(default_factory=list)
    edges: list = field(default_factory=list)
    skipped_files: int = 0   # non-document files we didn't turn into nodes
    truncated: bool = False  # hit max_nodes before finishing the walk

    def to_dict(self):
        return {
            "root": self.root,
            "nodes": self.nodes,
            "edges": self.edges,
            "counts": {
                "folders": sum(1 for n in self.nodes if n["type"] == "folder"),
                "docs": sum(1 for n in self.nodes if n["type"] == "doc"),
                "edges": len(self.edges),
                "skipped_files": self.skipped_files,
            },
            "truncated": self.truncated,
        }


def _rel_id(path: str, root: str) -> str:
    rel = os.path.relpath(path, root)
    return "." if rel == "." else rel.replace(os.sep, "/")


def scan_folder(root: str, max_nodes: int = 800) -> NodeMap:
    """Walk `root` and return a NodeMap. Raises ValueError if not a directory."""
    root = os.path.abspath(os.path.expanduser(root))
    if not os.path.isdir(root):
        raise ValueError(f"Not a directory: {root}")

    nm = NodeMap(root=root)
    seen = set()          # node ids
    doc_ids = set()       # doc node ids, for link resolution

    def add_node(node_id, label, ntype, **extra):
        if node_id in seen:
            return False
        if len(nm.nodes) >= max_nodes:
            nm.truncated = True
            return False
        seen.add(node_id)
        nm.nodes.append({"id": node_id, "label": label, "type": ntype, **extra})
        return True

    add_node(".", os.path.basename(root) or root, "folder")

    text_files = []  # (abs_path, node_id) to mine for links after the walk

    for dirpath, dirnames, filenames in os.walk(root, topdown=True):
        # prune hidden + known-noise dirs in place so walk skips them
        dirnames[:] = sorted(
            d for d in dirnames if not d.startswith(".") and d not in SKIP_DIRS
        )
        parent_id = _rel_id(dirpath, root)
        if parent_id not in seen:
            continue  # parent was dropped by max_nodes; skip subtree

        for d in dirnames:
            child_id = _rel_id(os.path.join(dirpath, d), root)
            if add_node(child_id, d, "folder"):
                nm.edges.append({"source": parent_id, "target": child_id, "kind": "contains"})

        for f in sorted(filenames):
            if f.startswith("."):
                continue
            ext = os.path.splitext(f)[1].lower()
            if ext not in DOC_EXTS:
                nm.skipped_files += 1
                continue
            fpath = os.path.join(dirpath, f)
            fid = _rel_id(fpath, root)
            try:
                size = os.path.getsize(fpath)
            except OSError:
                size = 0
            if add_node(fid, f, "doc", ext=ext, size=size):
                nm.edges.append({"source": parent_id, "target": fid, "kind": "contains"})
                doc_ids.add(fid)
                if ext in TEXT_EXTS and size <= MAX_TEXT_BYTES:
                    text_files.append((fpath, fid))

        if nm.truncated:
            break

    # Second pass: cross-document links from markdown/plain-text files.
    for fpath, fid in text_files:
        try:
            with open(fpath, "r", encoding="utf-8", errors="ignore") as fh:
                content = fh.read()
        except OSError:
            continue
        for target in _MD_LINK_RE.findall(content):
            if "://" in target:  # external URL, not a file
                continue
            resolved = os.path.normpath(os.path.join(os.path.dirname(fpath), target))
            tid = _rel_id(resolved, root)
            if tid in doc_ids and tid != fid:
                edge = {"source": fid, "target": tid, "kind": "links_to"}
                if edge not in nm.edges:
                    nm.edges.append(edge)

    return nm
