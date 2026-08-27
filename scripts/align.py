#!/usr/bin/env python3
"""N07 L-first path ranker. 12 Holmgren principles as If-Then-Root.
Does not rewrite CANON. Does not execute 12^12 nodes.
η unknown stays None. Rank key is gain/effort/time proxies only.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

FOUND = Path("/data/data/com.termux/files/home/src/openroot-foundation")
HARVEST = Path("/data/data/com.termux/files/home/openroot/harvest")
sys.path.insert(0, str(FOUND / "src"))
from openroot_canon import coord, eta, gamma, synergy, newton

assert coord(6, 1, 1.0) == 0.0

# Holmgren 12. Simultaneous web, not a queue.
P = {
    1: ("observe_interact", "N16"),
    2: ("catch_store_energy", "N01"),
    3: ("obtain_yield", "N02"),
    4: ("self_regulate", "N16"),
    5: ("renewable_services", "N07"),
    6: ("produce_no_waste", "N08"),
    7: ("patterns_to_details", "N10"),
    8: ("integrate_not_segregate", "N10"),
    9: ("small_slow", "N07"),
    10: ("value_diversity", "N05"),
    11: ("edges_marginal", "N12"),
    12: ("respond_to_change", "N16"),
}


def load_json(path: Path):
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def harvest_state() -> dict:
    index = HARVEST / "INDEX.jsonl"
    rows = 0
    if index.is_file():
        rows = sum(1 for l in index.read_text(encoding="utf-8").splitlines() if l.strip())
    shelf = {}
    for p in sorted((HARVEST / "shelves").glob("*.jsonl")) if (HARVEST / "shelves").is_dir() else []:
        shelf[p.stem] = sum(1 for l in p.read_text(encoding="utf-8").splitlines() if l.strip())
    tmp = HARVEST / "tmp_extract"
    tmp_b = tmp_n = 0
    if tmp.is_dir():
        for f in tmp.rglob("*"):
            if f.is_file():
                tmp_n += 1
                tmp_b += f.stat().st_size
    return {
        "index_rows": rows,
        "shelves": shelf,
        "tmp_files": tmp_n,
        "tmp_bytes": tmp_b,
        "cas": (HARVEST / "cas").is_dir(),
        "report": load_json(HARVEST / "SHELF_REPORT.json"),
    }


def score(useful: float, minutes: float) -> float:
    # gain / effort / time. Not N01 η. Denominator is human minutes.
    return useful / (minutes + 0.05)


def candidates(st: dict) -> list[dict]:
    tmp_b = st["tmp_bytes"]
    unsorted = st["shelves"].get("unsorted", 0)
    man = st["shelves"].get("man", 0)
    acts = [
        {
            "id": "free_scratch",
            "do": "rm -rf /data/data/com.termux/files/home/openroot/harvest/tmp_extract",
            "why": "42 MiB class already in CAS; scratch is waste after hang",
            "principles": [2, 6, 11],
            "useful": 0.95 if tmp_b > 1_000_000 else 0.05,
            "minutes": 0.2,
            "blocked": tmp_b == 0,
        },
        {
            "id": "do_not_reharvest_download",
            "do": "stop. Download already hung (603 rows)",
            "why": "second harvest is coordination cost, not yield",
            "principles": [4, 6, 9],
            "useful": 0.9,
            "minutes": 0.1,
            "blocked": False,
        },
        {
            "id": "leave_canon",
            "do": "import openroot_canon; do not write CANON.json",
            "why": "N16 locks do not rewrite themselves",
            "principles": [4, 5, 7],
            "useful": 0.88,
            "minutes": 0.1,
            "blocked": False,
        },
        {
            "id": "leave_home_git",
            "do": "do not git add -A from HOME or HOME/src",
            "why": "wrong tree is waste and lock dilution",
            "principles": [4, 7, 9],
            "useful": 0.86,
            "minutes": 0.1,
            "blocked": False,
        },
        {
            "id": "no_acre_mint",
            "do": "do not run acre_mint_claim.py",
            "why": "N02 money is not Γ; first INDEX row is a Download weed",
            "principles": [4, 3],
            "useful": 0.84,
            "minutes": 0.1,
            "blocked": False,
        },
        {
            "id": "no_solana",
            "do": "no program, no memo tonight",
            "why": "N10 book is chain.jsonl+cas, not a slot",
            "principles": [5, 9, 7],
            "useful": 0.8,
            "minutes": 0.1,
            "blocked": False,
        },
        {
            "id": "harvest_one_new_folder",
            "do": "python3 FOUND/scripts/harvest.py --root HARVEST --from ONE_NEW_DIR",
            "why": "yield is a new sha256, not a new manifesto",
            "principles": [3, 9, 11],
            "useful": 0.7,
            "minutes": 8.0,
            "blocked": False,
        },
        {
            "id": "ignore_man_pages",
            "do": "leave shelves/man.jsonl labeled; do not study 229 gh-*.1",
            "why": "edge junk already named; attention is the scarce joule",
            "principles": [6, 11, 9],
            "useful": 0.65 if man else 0.1,
            "minutes": 0.2,
            "blocked": man == 0,
        },
        {
            "id": "sample_unsorted_63",
            "do": "print 8 unsorted names from shelves/unsorted.jsonl",
            "why": "observe the remainder before inventing shelves",
            "principles": [1, 11],
            "useful": 0.55 if unsorted else 0.05,
            "minutes": 3.0,
            "blocked": unsorted == 0,
        },
        {
            "id": "measure_mass",
            "do": "append one mass_kg or room_dT to a hang note when a scale exists",
            "why": "N09; unknown stays None until weighed",
            "principles": [1, 3, 4],
            "useful": 0.6,
            "minutes": 20.0,
            "blocked": False,
        },
        {
            "id": "swarm_12_12",
            "do": "do not spawn 12^12 nodes on the A15",
            "why": "N14 sim score is not act η; heat not Γ",
            "principles": [4, 9],
            "useful": 0.5,
            "minutes": 0.1,
            "blocked": False,
        },
    ]
    out = []
    for a in acts:
        if a["blocked"]:
            continue
        a = dict(a)
        a["gain_per_min"] = round(score(a["useful"], a["minutes"]), 4)
        a["C"] = coord(6, 1, 1.0)
        a["S"] = synergy(6, 1.0, 6.0)
        a["eta_measured"] = eta(None, 0)  # honest: no joule meter on this act
        a["principles_named"] = [P[i][0] for i in a["principles"]]
        a["cite"] = sorted({P[i][1] for i in a["principles"]})
        out.append(a)
    out.sort(key=lambda x: -x["gain_per_min"])
    return out


def main() -> int:
    hits = newton("hang edges waste efficiency")
    st = harvest_state()
    ranked = candidates(st)
    top = ranked[0] if ranked else None
    doc = {
        "kind": "align_rank",
        "cite": "N01 N02 N03 N07 N08 N10 N11 N12 N14 N16",
        "coord": coord(6, 1, 1.0),
        "synergy_mult": synergy(6, 1.0, 6.0),
        "gamma": gamma(0, 1, 1, 1, 0, 0, 0),
        "R_assumed": 1.0,
        "not_claimed": [
            "measured human joules",
            "12^12 execution",
            "ACRE mint",
            "autonomous organism",
            "second lock",
        ],
        "newton_hits": hits,
        "state": st,
        "top": top,
        "ranked": ranked,
    }
    outp = HARVEST / "ALIGN.json"
    outp.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"wrote": str(outp), "top": top, "coord": 0.0}, indent=2))
    print("--- ranked gain/min ---")
    for i, a in enumerate(ranked, 1):
        print(f"{i:2} {a['gain_per_min']:7.3f}  {a['id']}  ::  {a['do']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
