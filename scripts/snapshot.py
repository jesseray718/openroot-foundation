#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, sys
from collections import defaultdict
from pathlib import Path
CHUNK = 1024 * 1024

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(CHUNK)
            if not b:
                break
            h.update(b)
    return h.hexdigest()

def classify(name: str, size: int) -> str:
    n = name.lower()
    if size <= 200 and n.endswith((".gz", ".tgz", ".tar")):
        return "empty_or_stub"
    if n.endswith(".deb"):
        return "foreign_deb"
    if n.endswith((".tar", ".gz", ".tgz", ".zip")):
        return "archive"
    if n.endswith((".py", ".sh")):
        return "code"
    if n.endswith((".md", ".txt", ".json", ".jsonl", ".csv")):
        return "docs"
    return "blob"

def action(kind: str) -> str:
    return {
        "empty_or_stub": "skip_empty",
        "foreign_deb": "leave_foreign",
        "archive": "unpack_once",
        "code": "keep_once",
        "docs": "keep_once",
        "blob": "keep_once",
    }.get(kind, "keep_once")

ap = argparse.ArgumentParser()
ap.add_argument("--from", dest="src", required=True)
ap.add_argument("--out", required=True)
args = ap.parse_args()
src, out = Path(args.src), Path(args.out)
if not src.is_dir():
    print("[FAIL]", src); sys.exit(1)
out.parent.mkdir(parents=True, exist_ok=True)
g = defaultdict(list)
seen = err = 0
for f in src.rglob("*"):
    if not f.is_file():
        continue
    seen += 1
    try:
        d = sha256_file(f)
        g[d].append({"path": str(f), "name": f.name, "bytes": f.stat().st_size})
    except OSError as e:
        err += 1
        g[f"err:{err}"].append({"path": str(f), "error": str(e)})
rows = []
uniq = extra = unpack = 0
for d, items in g.items():
    if str(d).startswith("err:"):
        rows.append({"error": True, "items": items})
        continue
    uniq += 1
    extra += len(items) - 1
    lead = items[0]
    kind = classify(lead["name"], lead["bytes"])
    act = action(kind)
    if act == "unpack_once":
        unpack += 1
    rows.append({"sha256": d, "bytes": lead["bytes"], "kind": kind, "action": act,
                 "copies": len(items), "names": [i["name"] for i in items]})
summ = {"cite": "N08 N12", "from": str(src), "seen_files": seen, "unique_blobs": uniq,
        "duplicate_extra": extra, "err": err, "convert_archives": unpack}
out.write_text(json.dumps(summ, indent=2) + "\n" +
               "".join(json.dumps(r, sort_keys=True) + "\n" for r in rows), encoding="utf-8")
print(json.dumps(summ, indent=2))
print("wrote", out)
