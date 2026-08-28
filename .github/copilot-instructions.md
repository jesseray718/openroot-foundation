# Copilot / inference instructions

This repo is the locked foundation for OpenRoot (N00–N16 in `canon/CANON.json`).

## Core Rules

- **Cite, don't rewrite.** Reference N00–N16 by id. Do not paraphrase the lock text.
- **Import when needed.** Use `src/openroot_canon` for `coord()`, `newton()`, `derive()`, `eta()`, `gamma()`.
- **Match then return.** Match a postulate first; return its id and lock text. Skip recomputation (N00).
- **coord(N,T,R=1) = 0.0 for T≥1.** This is identically true per N03: when R=1, (1-R)^T = 0. If your code prints otherwise, your code is wrong.
- **Small patches only.** Prefer incremental fixes. Do not add a second CANON.

## Rules for New Terms

- Three real uses before locking; otherwise they are weeds (N11).
- If a locked name already says it, use that name.

## Deployment Notes

- **Absolute paths only** when talking to Jesse on Termux (no tilde).
- **Serve the least-capable node first** (N07).
- **License:** CC-BY-SA-4.0 docs, GPL-3.0 code. No patents (N15).
