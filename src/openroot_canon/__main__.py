from __future__ import annotations
import argparse
import json
from .laws import coord, eta, gamma, landauer, synergy
from .newton import derive, load_canon, newton


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="openroot_canon")
    sub = p.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("newton"); n.add_argument("query")
    d = sub.add_parser("derive"); d.add_argument("utterance")
    sub.add_parser("list")
    e = sub.add_parser("eval")
    e.add_argument("fn", choices=["coord", "eta", "gamma", "synergy", "landauer"])
    e.add_argument("--N", type=float, default=6)
    e.add_argument("--T", type=float, default=1)
    e.add_argument("--R", type=float, default=1.0)
    e.add_argument("--B", type=float, default=6)
    e.add_argument("--useful", type=float, default=0)
    e.add_argument("--human", type=float, default=0)
    e.add_argument("--Y", type=float, default=0)
    e.add_argument("--L", type=float, default=1)
    e.add_argument("--P", type=float, default=1)
    e.add_argument("--F", type=float, default=1)
    e.add_argument("--Jh", type=float, default=0)
    e.add_argument("--Je", type=float, default=0)
    e.add_argument("--C", type=float, default=0)
    e.add_argument("--bits", type=float, default=1)
    e.add_argument("--Tkelvin", type=float, default=300)
    args = p.parse_args(argv)
    if args.cmd == "newton":
        print(json.dumps(newton(args.query), indent=2, ensure_ascii=False)); return 0
    if args.cmd == "derive":
        print(json.dumps(derive(args.utterance), indent=2, ensure_ascii=False)); return 0
    if args.cmd == "list":
        print(json.dumps([{"id": x["id"], "name": x["name"]} for x in load_canon()["postulates"]], indent=2)); return 0
    if args.cmd == "eval":
        if args.fn == "coord":
            print(coord(args.N, args.T, args.R))
        elif args.fn == "eta":
            print(eta(args.useful, args.human))
        elif args.fn == "gamma":
            print(gamma(args.Y, args.L, args.P, args.F, args.Jh, args.Je, args.C))
        elif args.fn == "synergy":
            print(synergy(args.N, args.R, args.B))
        else:
            print(landauer(args.bits, args.Tkelvin))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
