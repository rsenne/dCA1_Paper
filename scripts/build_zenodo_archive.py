#!/usr/bin/env python
"""Assemble the Zenodo deposit: the data this repo cannot carry, plus the code.

The repository already tracks the ~26 MB of processed tables the published
figures are plotted from. This script packages everything else needed to
reproduce the work from scratch, as a small number of zip files:

    dca1_collections.zip           per-session pickled collections
    dca1_cell_traces.zip           per-animal Inscopix trace exports
    dca1_derived_intermediates.zip trace exports + event times + freeze vectors
    dca1_behavior.zip              AnyMaze freezing scores
    dca1_code_<sha>.zip            snapshot of this repository at HEAD
    MANIFEST.sha256                checksum and size of every file above
    README.md                      how to use the deposit
    zenodo_metadata.json           metadata for the Zenodo form or API

Usage
-----
    python scripts/build_zenodo_archive.py --dry-run
    python scripts/build_zenodo_archive.py --out D:/zenodo_dca1
    python scripts/build_zenodo_archive.py --out D:/zenodo_dca1 --only code

Nothing is uploaded. Review the staging directory before depositing: a
published Zenodo DOI cannot be withdrawn.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import zipfile
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

SESSIONS = ("hab", "fc", "cxta", "cxtb")

# Not part of the deposit: excluded animals, scratch folders, derived images.
EXCLUDE_DIRS = {
    "bad_donotuse", "bad mice", "summary_images", "dontuse", "do_not_use",
    "combined_outputs",
}

COMPONENTS = ("collections", "cell_traces", "intermediates", "behavior", "code")

CITATION = {
    "title": (
        "Data and code for: A hippocampal astrocytic sequence emerges during "
        "learning and memory"
    ),
    "upload_type": "dataset",
    "creators": [
        {"name": "Senne, Ryan"},
        {"name": "Suthard, Rebecca"},
        {"name": "Monasterio, Amy"},
    ],
    "license": "cc-by-4.0",
    "keywords": [
        "astrocyte", "hippocampus", "CA1", "calcium imaging", "one-photon",
        "Inscopix", "fear conditioning", "memory", "reproducibility",
    ],
    "related_identifiers": [
        {
            "relation": "isSupplementTo",
            "identifier": "https://github.com/rsenne/dCA1_Paper",
            "resource_type": "software",
        }
    ],
}

DESCRIPTION = """\
<p>One-photon (Inscopix) calcium imaging of dorsal CA1 astrocytes across four
sessions: habituation, contextual fear conditioning, and two recall contexts
(A and B). This deposit contains the imaging data and a snapshot of the
analysis code, so the published figures can be regenerated end to end.</p>

<p><strong>Files</strong></p>
<ul>
<li><code>dca1_code_&lt;sha&gt;.zip</code> &mdash; the analysis repository,
including the ~26 MB of processed tables the figures are plotted from. Most
figures can be reproduced from this file alone.</li>
<li><code>dca1_collections.zip</code> &mdash; per-session collections of all
animals (accepted traces, rejected indices, timestamps, detected events,
cross-session registration tables). Python pickles; require the bundled
<code>onep</code> package to load.</li>
<li><code>dca1_cell_traces.zip</code> &mdash; per-animal Inscopix trace
exports.</li>
<li><code>dca1_derived_intermediates.zip</code> &mdash; per-animal accepted
traces, detected event times, and freezing vectors, as consumed by several
supplementary analyses. Regenerable from the collections.</li>
<li><code>dca1_behavior.zip</code> &mdash; AnyMaze freezing scores.</li>
<li><code>MANIFEST.sha256</code> &mdash; checksums for every file.</li>
</ul>

<p>See <code>README.md</code> in this deposit for setup, and the code
repository at <a href="https://github.com/rsenne/dCA1_Paper">github.com/rsenne/dCA1_Paper</a>
for issues and updates.</p>
"""


def sha256(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def human(n: float) -> str:
    for unit in ("B", "KiB", "MiB", "GiB"):
        if n < 1024 or unit == "GiB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} GiB"


def tree_size(root: Path) -> int:
    return sum(f.stat().st_size for f in root.rglob("*") if f.is_file())


def excluded(path: Path) -> bool:
    return any(p.strip().lower() in EXCLUDE_DIRS for p in path.parts)


def git_sha() -> str:
    try:
        out = subprocess.run(
            ["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, check=True,
        )
        return out.stdout.strip()
    except Exception:
        return "nogit"


def write_zip(target: Path, entries: list[tuple[Path, str]]) -> None:
    """Write a deflated zip from (source_file, arcname) pairs."""
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED, compresslevel=6,
                         allowZip64=True) as zf:
        for src, arc in entries:
            zf.write(src, arcname=arc)


# --------------------------------------------------------------------------
# Component planning
# --------------------------------------------------------------------------

def plan_collections(root: Path):
    entries, missing = [], []
    for s in SESSIONS:
        f = root / "Dill" / f"collection_{s}_allmice.pkl"
        (entries if f.is_file() else missing).append(
            (f, f"Dill/{f.name}") if f.is_file() else f
        )
    return entries, missing


def plan_cell_traces(root: Path):
    src = root / "Cell_Traces"
    if not src.is_dir():
        return [], [src]
    entries = []
    for f in sorted(src.rglob("*")):
        if f.is_file() and not excluded(f.relative_to(src)):
            entries.append((f, f"Cell_Traces/{f.relative_to(src).as_posix()}"))
    return entries, []


def plan_intermediates(inter: Path | None):
    if inter is None:
        return [], ["derived intermediates (not found)"]
    entries = []
    for sub in ("fc_traces_csv", "cxta_traces_csv", "cxtb_traces_csv",
                "hab_traces_csv", "dlc"):
        d = inter / sub
        if not d.is_dir():
            continue
        for f in sorted(d.rglob("*")):
            if f.is_file():
                entries.append((f, f"Derived_Exports/{sub}/{f.relative_to(d).as_posix()}"))
    # Small shared tables at the root of the intermediates tree.
    for name in ("Time.csv", "Freezing_Metrics.csv", "freeze_event_analysis.csv"):
        f = inter / name
        if f.is_file():
            entries.append((f, f"Derived_Exports/{name}"))
    return entries, []


def plan_behavior(root: Path):
    d = root / "Anymaze"
    if not d.is_dir():
        return [], [d]
    return [(f, f"Anymaze/{f.name}") for f in sorted(d.glob("*.csv"))], []


def plan_code():
    """Repository snapshot from git, so it matches a real commit exactly."""
    try:
        out = subprocess.run(
            ["git", "-C", str(REPO), "ls-files", "-z"],
            capture_output=True, check=True,
        )
    except Exception as exc:
        return [], [f"git ls-files failed: {exc}"]
    entries = []
    for rel in out.stdout.decode().split("\0"):
        if not rel:
            continue
        f = REPO / rel
        if f.is_file():
            entries.append((f, f"dCA1_Paper/{rel}"))
    return entries, []


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=Path, help="staging directory")
    ap.add_argument("--dry-run", action="store_true",
                    help="report what would be built, write nothing")
    ap.add_argument("--only", nargs="+", choices=COMPONENTS,
                    help="build only these components")
    args = ap.parse_args()

    try:
        from onep import paths
    except ImportError as exc:
        print(f"cannot import onep ({exc}); run `pip install -e .`", file=sys.stderr)
        return 1

    root = paths.data_root(required=False)
    inter = paths.intermediates(required=False)
    sha = git_sha()

    print(f"imaging data  : {root or '[not found]'}")
    print(f"intermediates : {inter or '[not found]'}")
    print(f"code revision : {sha}\n")

    if root is None and (not args.only or set(args.only) - {"code"}):
        print("The imaging dataset was not found; only the code component can be\n"
              "built. Set DCA1_DATA_ROOT (see data/README.md).", file=sys.stderr)
        if not args.only:
            return 1

    wanted = set(args.only) if args.only else set(COMPONENTS)
    plans: dict[str, tuple[str, list, list]] = {}

    if "collections" in wanted and root is not None:
        e, m = plan_collections(root); plans["collections"] = ("dca1_collections.zip", e, m)
    if "cell_traces" in wanted and root is not None:
        e, m = plan_cell_traces(root); plans["cell_traces"] = ("dca1_cell_traces.zip", e, m)
    if "intermediates" in wanted:
        e, m = plan_intermediates(inter)
        plans["intermediates"] = ("dca1_derived_intermediates.zip", e, m)
    if "behavior" in wanted and root is not None:
        e, m = plan_behavior(root); plans["behavior"] = ("dca1_behavior.zip", e, m)
    if "code" in wanted:
        e, m = plan_code(); plans["code"] = (f"dca1_code_{sha}.zip", e, m)

    grand = 0
    for name, (zipname, entries, missing) in plans.items():
        raw = sum(src.stat().st_size for src, _ in entries)
        grand += raw
        print(f"  {zipname:34s} {len(entries):5d} files  {human(raw):>10s} uncompressed")
        for m in missing:
            print(f"      MISSING: {m}")
    print(f"\n{human(grand)} uncompressed across {len(plans)} archive(s)")
    print("CSV-heavy archives typically compress 3-10x.")

    if args.dry_run:
        print("\n--dry-run: nothing written")
        return 0

    if args.out is None:
        print("\nerror: --out is required unless --dry-run", file=sys.stderr)
        return 1

    out = args.out.expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    print(f"\nbuilding in {out}")

    built = []
    for name, (zipname, entries, _) in plans.items():
        if not entries:
            print(f"  skip {zipname} (nothing to add)")
            continue
        target = out / zipname
        if target.exists():
            print(f"  exists {zipname} (delete to rebuild)")
        else:
            print(f"  writing {zipname} ({len(entries)} files)...", flush=True)
            write_zip(target, entries)
        size = target.stat().st_size
        built.append((target, size))
        print(f"    {human(size)}")

    lines = ["# SHA-256 manifest for the dCA1 Zenodo deposit",
             f"# code revision: {sha}",
             "#"]
    for target, size in built:
        lines.append(f"{sha256(target)}  {size}  {target.name}")
    (out / "MANIFEST.sha256").write_text("\n".join(lines) + "\n",
                                         encoding="utf-8", newline="\n")

    (out / "README.md").write_text(
        deposit_readme(sha, [t.name for t, _ in built]),
        encoding="utf-8", newline="\n",
    )

    meta = dict(CITATION)
    meta["description"] = DESCRIPTION
    meta["publication_date"] = date.today().isoformat()
    meta["version"] = sha
    (out / "zenodo_metadata.json").write_text(
        json.dumps({"metadata": meta}, indent=2) + "\n",
        encoding="utf-8", newline="\n",
    )

    total = sum(s for _, s in built)
    print(f"\n{len(built)} archive(s), {human(total)} compressed")
    print(f"  MANIFEST.sha256 / README.md / zenodo_metadata.json written")
    print(f"\nReview {out} before uploading. A published DOI cannot be withdrawn.")
    print("After publishing, record the DOI in README.md and data/README.md.")
    return 0


def deposit_readme(sha: str, names: list[str]) -> str:
    listing = "\n".join(f"- `{n}`" for n in names)
    return f"""\
# A hippocampal astrocytic sequence emerges during learning and memory

Data and analysis code. Code revision `{sha}`; the current version is at
https://github.com/rsenne/dCA1_Paper

## Files

{listing}

## Reproducing the figures

Most figures need only the code archive, which includes the processed tables
they are plotted from.

```bash
unzip dca1_code_{sha}.zip && cd dCA1_Paper
python -m venv .venv && source .venv/bin/activate   # Scripts/activate on Windows
pip install -r requirements.txt
python scripts/verify_data.py          # checks the bundled processed data
jupyter lab notebooks/figures/
```

## Using the imaging data

Extract the data archives into one directory and point the code at it:

```bash
mkdir dCA1_Clean_Data && cd dCA1_Clean_Data
unzip ../dca1_collections.zip
unzip ../dca1_cell_traces.zip
unzip ../dca1_behavior.zip
unzip ../dca1_derived_intermediates.zip     # creates Derived_Exports/
cd ..

export DCA1_DATA_ROOT=$PWD/dCA1_Clean_Data
python scripts/verify_data.py --check-upstream
```

`Derived_Exports/` is found automatically once `DCA1_DATA_ROOT` is set. To keep
it elsewhere, set `DCA1_INTERMEDIATES` to its path.

Resulting layout:

```
dCA1_Clean_Data/
├── Dill/collection_{{hab,fc,cxta,cxtb}}_allmice.pkl
├── Cell_Traces/{{animal}}_traces/{{animal}}_{{session}}_traces.csv
├── Anymaze/{{session}}_freezing.csv
└── Derived_Exports/
    ├── {{session}}_traces_csv/    accepted traces, event times, freeze vectors
    ├── dlc/                     DeepLabCut pose output
    └── Time.csv
```

Sessions are `hab`, `fc`, `cxta`, `cxtb`. Animals are `astroF*` / `astroM*`,
where F/M denotes sex.

## Loading a collection

The collections are pickled Python objects and need the bundled `onep` package:

```python
import pickle
from onep import paths

with open(paths.collection("fc"), "rb") as f:
    collection = pickle.load(f)

collection.animals["astroF9"].accepted_traces
```

## Verifying integrity

```bash
sha256sum -c MANIFEST.sha256
```

## Scope

`README.md` in the code archive maps every figure to the notebook that makes
it and records which notebooks were verified by execution. Six supplementary
notebooks read `Derived_Exports/` but still contain absolute paths from the
machines they were written on; they are included for completeness and are
documented as such rather than silently shipped as reproducible.

## Licence

CC BY 4.0. Please cite both the paper and this deposit.
"""


if __name__ == "__main__":
    raise SystemExit(main())
