#!/usr/bin/env python
"""Export per-animal accepted traces from a session collection to CSV.

These CSVs are the input to the Julia sequence detector (see julia/README.md)
and to the generative peak-time model. They are derived intermediates, so they
are written to results/ rather than into the committed data tier.

Usage
-----
    python scripts/Export_Files_Rui.py                 # fear conditioning
    python scripts/Export_Files_Rui.py --session cxta
    python scripts/Export_Files_Rui.py --session hab --out /path/to/dir

Requires the imaging tier; see data/README.md.
"""

from __future__ import annotations

import argparse
import pickle as pkl
from pathlib import Path

from onep import paths

SESSIONS = ("hab", "fc", "cxta", "cxtb")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--session", default="fc", choices=SESSIONS,
                    help="session to export (default: fc)")
    ap.add_argument("--out", type=Path, default=None,
                    help="output directory (default: results/exports/<session>)")
    args = ap.parse_args()

    src = paths.collection(args.session)
    out = args.out.expanduser() if args.out else \
        paths.repo_root() / "results" / "exports" / args.session
    out.mkdir(parents=True, exist_ok=True)

    print(f"reading  {src}")
    with open(src, "rb") as f:
        collection = pkl.load(f)

    n = 0
    for animal, obj in collection.animals.items():
        target = out / f"{animal}_{args.session}_accepted_traces.csv"
        obj.accepted_traces.to_csv(target, index=False)
        print(f"  wrote  {target.name}")
        n += 1

    print(f"\n{n} animal(s) exported to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
