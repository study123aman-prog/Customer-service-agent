"""
knowledge.py — loads the knowledge base and does simple, transparent retrieval.

In production, retrieval is hybrid dense+sparse with a cross-encoder re-rank
(see docs/knowledge-base). Here we implement a DETERMINISTIC keyword-overlap
scorer behind the same idea: given a query, return the top-k most relevant KB
entries. The important design property preserved from the docs is that FACTS come
from the entry's `structured` field, never from prose paraphrase — so the demo can
answer with exact numbers and never "make up" a rate.
"""

import json
import re
from .config import KB_PATH


def _load():
    try:
        with open(KB_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return []


_ENTRIES = _load()
_STOP = {"the", "a", "an", "is", "are", "of", "for", "to", "my", "i", "what",
         "how", "do", "does", "can", "you", "me", "and", "or", "in", "on", "it"}


def _tokens(text):
    return [t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in _STOP]


def retrieve(query, top_k=3):
    """Return up to top_k KB entries scored by keyword overlap (highest first)."""
    q = set(_tokens(query))
    if not q:
        return []
    scored = []
    for e in _ENTRIES:
        hay = " ".join([e.get("title", ""), e.get("body", ""),
                        " ".join(e.get("keywords", []))]).lower()
        toks = set(_tokens(hay))
        overlap = len(q & toks)
        if overlap:
            scored.append((overlap, e))
    scored.sort(key=lambda x: (-x[0], x[1]["id"]))   # deterministic tie-break by id
    return [e for _, e in scored[:top_k]]


def get(entry_id):
    for e in _ENTRIES:
        if e["id"] == entry_id:
            return e
    return None


def fact(entry_id, key, default=None):
    """Fetch a single structured fact (the only way the demo states numbers)."""
    e = get(entry_id)
    if not e:
        return default
    return e.get("structured", {}).get(key, default)


def count():
    return len(_ENTRIES)
