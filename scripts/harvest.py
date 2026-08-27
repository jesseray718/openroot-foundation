#!/usr/bin/env python3
"""
N08 + N12: unpack archives, keep each unique byte string once.
Does not rewrite foundation. Does not mint a public chain.
CAS path: <root>/cas/aa/bb/<sha256>
Index:    <root>/INDEX.jsonl
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tarfile
import zipfile
from pathlib import Path

CHUNK = 1024 * 1024
ARCH_SUFFIX = (".tar", ".tar.gz", ".tgz", ".tar.bz2", ".tar.xz", ".gz", ".zip")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(CHUNK)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def cas_path(root: Path, digest: str) -> Path:
    return root / "cas" / digest[:2] / digest[2:4] / digest


def already(root: Path, digest: str) -> bool:
    return cas_path(root, digest).is_file()


def store(root: Path, src: Path, digest: str) -> Path:
    dest = cas_path(root, digest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        dest.write_bytes(src.read_bytes())
    return dest


def append_index(root: Path, row: dict) -> None:
    with (root / "INDEX.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")


def safe_members(tf: tarfile.TarFile):
    for m in tf.getmembers():
        name = m.name.replace("\\", "/")
        if name.startswith("/") or ".." in Path(name).parts:
            continue
        yield m


def harvest_file(root: Path, path: Path, origin: str) -> dict:
    digest = sha256_file(path)
    new = not already(root, digest)
    if new:
        store(root, path, digest)
    row = {
        "sha256": digest,
        "bytes": path.stat().st_size,
        "name": path.name,
        "origin": origin,
        "new": new,
    }
    append_index(root, row)
    return row


def harvest_archive(root: Path, archive: Path, tmp: Path) -> list[dict]:
    dest = tmp / archive.stem
    dest.mkdir(parents=True, exist_ok=True)
    rows = []
    try:
        if zipfile.is_zipfile(archive):
            with zipfile.ZipFile(archive) as z:
                z.extractall(dest)
        elif tarfile.is_tarfile(archive):
            with tarfile.open(archive) as t:
                t.extractall(dest, members=safe_members(t))
        else:
            return [harvest_file(root, archive, str(archive))]
    except Exception as e:
        return [{"origin": str(archive), "error": str(e), "new": False}]
    for p in dest.rglob("*"):
        if p.is_file():
            rows.append(harvest_file(root, p, f"{archive}::{p.relative_to(dest)}"))
    return rows


def main() -> int:
    p = argparse.ArgumentParser(description="Harvest unique bytes. N08.")
    p.add_argument("--root", required=True, help="CAS root, absolute")
    p.add_argument("--from", dest="src", required=True, help="folder of tars/files")
    p.add_argument("--tmp", default="", help="scratch extract dir")
    args = p.parse_args()
    root = Path(args.root)
    src = Path(args.src)
    tmp = Path(args.tmp) if args.tmp else root / "tmp_extract"
    root.mkdir(parents=True, exist_ok=True)
    tmp.mkdir(parents=True, exist_ok=True)
    files = []
    if src.is_file():
        files = [src]
    else:
        for p in sorted(src.rglob("*")):
            if p.is_file():
                files.append(p)
    stats = {"seen": 0, "new": 0, "dup": 0, "err": 0}
    for f in files:
        if f.suffix.lower() in {".gz", ".tgz", ".zip"} or any(str(f).endswith(s) for s in ARCH_SUFFIX):
            rows = harvest_archive(root, f, tmp)
        else:
            rows = [harvest_file(root, f, str(f))]
        for r in rows:
            stats["seen"] += 1
            if r.get("error"):
                stats["err"] += 1
            elif r.get("new"):
                stats["new"] += 1
            else:
                stats["dup"] += 1
    print(json.dumps(stats, indent=2))
    print("index", root / "INDEX.jsonl")
    print("cas", root / "cas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
