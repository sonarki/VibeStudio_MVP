"""docmap: scan a documents folder and build a node map (graph)."""

from .scanner import scan_folder, NodeMap

__all__ = ["scan_folder", "NodeMap"]
