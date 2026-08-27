"""Newton chain — match a locked postulate, skip the essay."""
from __future__ import annotations
import json
import re
from pathlib import Path

_CANON = Path(__file__).resolve().parents[2] / "canon" / "CANON.json"
_REDIRECTS = {
    "solana": "N10",
    "bitcoin": "N10",
    "ethereum": "N10",
    "blockchain": "N10",
    "miner": "N10",
    "gas": "N10",
    "money": "N02",
    "price": "N02",
    "profit": "N01",
    "efficiency": "N14",
    "feedback": "N16",
    "selfregulation": "N16",
}


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def load_canon() -> dict:
    return json.loads(_CANON.read_text(encoding="utf-8"))


def postulate(pid: str) -> dict | None:
    for p in load_canon()["postulates"]:
        if p["id"] == pid or p["name"] == pid:
            return {"id": p["id"], "name": p["name"], "lock": p["lock"]}
    return None


def newton(query: str) -> list[dict]:
    q = _norm(query)
    hits: list[dict] = []
    for word in q.split():
        target = _REDIRECTS.get(word)
        if target:
            h = postulate(target)
            if h:
                hits.append(h)
    for p in load_canon()["postulates"]:
        keys = {p["id"].lower(), p["name"].lower(), str(p.get("symbol", "")).lower()}
        if any(k and (k in q.split() or (len(k) > 2 and k in q)) for k in keys):
            hits.append({"id": p["id"], "name": p["name"], "lock": p["lock"]})
    seen = set()
    out = []
    for h in hits:
        if h["lock"] in seen:
            continue
        seen.add(h["lock"])
        out.append(h)
    return out


def derive(utterance: str) -> dict:
    hits = newton(utterance)
    if hits:
        return {"operator": "A1", "path": "Newton", "hits": hits}
    return {
        "operator": "A1",
        "path": "underived",
        "utterance": utterance,
        "next": "cite an existing N-id or pay need_gate",
    }
