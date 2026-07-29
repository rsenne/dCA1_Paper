#!/usr/bin/env python
"""Assemble the Zenodo deposit for the imaging tier of the dCA1 dataset.

The repository already carries the 26 MB of processed tables the figures read.
What it cannot carry is the imaging tier -- the pickled per-session collections
and the raw Inscopix cell traces (~940 MB). This script gathers those into a
staging directory with a checksum manifest, a README, and Zenodo metadata, so
the deposit is reproducible rather than a hand-assembled zip.

Typical use::

    python scripts/build_zenodo_archive.py --dry-run     # see what it would do
    python scripts/build_zenodo_archive.py --out D:/zenodo_dca1
    # inspect, then upload the contents of that directory to Zenodo

By default the cell traces are packed into one .tar.gz per animal, which keeps
the file count low enough for Zenodo's web uploader while staying inspectable.
Pass --no-archive-traces to copy them as loose files instead.

Nothing is uploaded; this only stages files locally. Review the staged
directory before depositing anything, since a Zenodo record with a DOI cannot
be withdrawn.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tarfile
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

SESSIONS = ("hab", "fc", "cxta", "cxtb")

# Directories under Cell_Traces/ that are not part of the deposit: excluded
# animals, scratch folders, and derived image stacks that are not trace data.
# Matched case-insensitively against the directory name.
EXCLUDE_TRACE_DIRS = {
    "bad_donotuse",
    "bad mice",
    "bad micem",
    "summary_images",
    "dontuse",
    "do_not_use",
}

# Filled in on acceptance; kept here so the deposit metadata has one home.
CITATION = {
    "title": (
        "Imaging dataset for: A hippocampal astrocytic sequence emerges "
        "during learning and memory"
    ),
    "upload_type": "dataset",
    "creators": [
        {"name": "Senne, Ryan"},
        {"name": "Suthard, Rebecca"},
        {"name": "Monasterio, Amy"},
    ],
    "license": "cc-by-4.0",
    "keywords": [
        "astrocyte", "hippocampus", "CA1", "calcium imaging",
        "one-photon", "Inscopix", "fear conditioning", "memory",
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
(A and B).</p>

<p>This deposit holds the <strong>imaging tier</strong> of the dataset: the
per-session processed collections and the per-animal cell traces. The smaller
post-hoc tables that the published figures are plotted from are distributed
with the analysis code at <a
href="https://github.com/rsenne/dCA1_Paper">github.com/rsenne/dCA1_Paper</a>,
so the figures can be reproduced without downloading this archive.</p>

<p>Contents:</p>
<ul>
<li><code>Dill/collection_{session}_allmice.pkl</code> &mdash; per-session
collections of all animals: accepted traces, rejected indices, timestamps,
detected events, and cross-session registration tables.</li>
<li><code>Cell_Traces/</code> &mdash; per-animal Inscopix trace exports, one
gzipped tar per animal.</li>
<li><code>Anymaze/</code> &mdash; freezing scores per animal and session.</li>
<li><code>MANIFEST.sha256</code> &mdash; SHA-256 and size of every file.</li>
</ul>

<p>The pickles are Python objects and require the <code>onep</code> package
from the code repository to load. See that repository's
<code>data/README.md</code> for the directory layout the code expects and
<code>onep/paths.py</code> for how to point the analysis at this data after
download.</p>
"""

README = """\
# Imaging dataset — dCA1 astrocyte sequences

Companion data for the analysis code at
https://github.com/rsenne/dCA1_Paper

## What this is

One-photon calcium imaging of dorsal CA1 astrocytes across habituation (`hab`),
contextual fear conditioning (`fc`), and two recall contexts (`cxta`, `cxtb`).
Animals are named `astroF*` / `astroM*`, where F/M denotes sex.

This archive is the **imaging tier**. The processed tables the published
figures are plotted from ship with the code repository, so you do not need this
archive to reproduce the figures — only to rebuild those tables from traces or
to run the analyses that operate on full traces.

## Contents

```
Dill/collection_{hab,fc,cxta,cxtb}_allmice.pkl   per-session collections
Cell_Traces/{animal}_traces.tar.gz               per-animal Inscopix traces
Anymaze/                                         freezing scores
MANIFEST.sha256                                  checksums for everything
```

## Verifying

```bash
sha256sum -c MANIFEST.sha256
```

## Using it

```bash
git clone https://github.com/rsenne/dCA1_Paper && cd dCA1_Paper
pip install -r requirements.txt

# extract the traces next to the collections
mkdir -p /path/to/dCA1_Clean_Data/Cell_Traces
for f in Cell_Traces/*.tar.gz; do tar -xzf "$f" -C /path/to/dCA1_Clean_Data/Cell_Traces; done

export DCA1_DATA_ROOT=/path/to/dCA1_Clean_Data
python scripts/verify_data.py --check-upstream
```

The collections are pickled Python objects and need the `onep` package to load:

```python
import pickle
from onep import paths

with open(paths.collection("fc"), "rb") as f:
    collection = pickle.load(f)

collection.animals["astroF9"].accepted_traces
```

## Licence

CC BY 4.0. Please cite both the paper and this deposit.
"""


def sha256(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def human(n: int) -> str:
    for unit in ("B", "KiB", "MiB", "GiB"):
        if n < 1024 or unit == "GiB":
            return f"{n:.1f} {unit}" if unit != "B" else f"{n} B"
        n /= 1024
    return f"{n:.1f} GiB"


def plan(root: Path, archive_traces: bool):
    """Return [(kind, source, dest_relpath, size)] for the deposit."""
    items = []

    for session in SESSIONS:
        src = root / "Dill" / f"collection_{session}_allmice.pkl"
        if src.is_file():
            items.append(("copy", src, f"Dill/{src.name}", src.stat().st_size))
        else:
            items.append(("MISSING", src, f"Dill/{src.name}", 0))

    traces_root = root / "Cell_Traces"
    if traces_root.is_dir():
        for animal_dir in sorted(p for p in traces_root.iterdir() if p.is_dir()):
            if animal_dir.name.strip().lower() in EXCLUDE_TRACE_DIRS:
                items.append(("skip", animal_dir, f"Cell_Traces/{animal_dir.name}", 0))
                continue
            size = sum(f.stat().st_size for f in animal_dir.rglob("*") if f.is_file())
            if archive_traces:
                items.append(("tar", animal_dir,
                              f"Cell_Traces/{animal_dir.name}.tar.gz", size))
            else:
                for f in sorted(animal_dir.rglob("*")):
                    if f.is_file():
                        rel = f.relative_to(traces_root).as_posix()
                        items.append(("copy", f, f"Cell_Traces/{rel}",
                                      f.stat().st_size))
    else:
        items.append(("MISSING", traces_root, "Cell_Traces/", 0))

    anymaze = root / "Anymaze"
    if anymaze.is_dir():
        for f in sorted(anymaze.glob("*.csv")):
            items.append(("copy", f, f"Anymaze/{f.name}", f.stat().st_size))

    return items


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=Path,
                    help="staging directory (required unless --dry-run)")
    ap.add_argument("--dry-run", action="store_true",
                    help="list what would be staged, copy nothing")
    ap.add_argument("--no-archive-traces", action="store_true",
                    help="copy cell traces as loose files instead of per-animal tarballs")
    args = ap.parse_args()

    try:
        from onep import paths
    except ImportError as exc:
        print(f"cannot import onep ({exc}); run `pip install -e .`", file=sys.stderr)
        return 1

    root = paths.data_root(required=False)
    if root is None:
        print(
            "The imaging dataset was not found, so there is nothing to stage.\n"
            "Set DCA1_DATA_ROOT or config.ini first (see data/README.md).",
            file=sys.stderr,
        )
        return 1

    print(f"source: {root}\n")
    items = plan(root, archive_traces=not args.no_archive_traces)

    missing = [i for i in items if i[0] == "MISSING"]
    skipped = [i for i in items if i[0] == "skip"]
    real = [i for i in items if i[0] not in ("MISSING", "skip")]
    total = sum(i[3] for i in real)

    for kind, src, dest, size in real:
        print(f"  {kind:4s} {human(size):>10s}  {dest}")
    for _, src, dest, _ in skipped:
        print(f"  skip             --  {dest}   (excluded from deposit)")
    for _, src, dest, _ in missing:
        print(f"  MISSING              {dest}   (expected at {src})")

    print(f"\n{len(real)} items, {human(total)} uncompressed"
          + (f"  ({len(skipped)} excluded)" if skipped else ""))
    if missing:
        print(f"WARNING: {len(missing)} expected item(s) missing", file=sys.stderr)

    if args.dry_run:
        print("\n--dry-run: nothing written")
        return 1 if missing else 0

    if args.out is None:
        print("\nerror: --out is required unless --dry-run", file=sys.stderr)
        return 1

    out = args.out.expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    print(f"\nstaging into {out}")

    manifest = []
    for kind, src, dest, _ in real:
        target = out / dest
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            print(f"  skip (exists)  {dest}")
        elif kind == "tar":
            print(f"  tar   {dest}")
            with tarfile.open(target, "w:gz") as tf:
                tf.add(src, arcname=src.name)
        else:
            print(f"  copy  {dest}")
            shutil.copy2(src, target)
        manifest.append((sha256(target), target.stat().st_size, dest))

    lines = [f"{d}  {dest}" for d, _, dest in manifest]
    (out / "MANIFEST.sha256").write_text("\n".join(lines) + "\n",
                                        encoding="utf-8", newline="\n")
    (out / "README.md").write_text(README, encoding="utf-8", newline="\n")

    meta = dict(CITATION)
    meta["description"] = DESCRIPTION
    meta["publication_date"] = date.today().isoformat()
    (out / "zenodo_metadata.json").write_text(
        json.dumps({"metadata": meta}, indent=2) + "\n",
        encoding="utf-8", newline="\n",
    )

    staged = sum(s for _, s, _ in manifest)
    print(
        f"\nstaged {len(manifest)} files, {human(staged)}\n"
        f"  MANIFEST.sha256      checksums\n"
        f"  README.md            deposit README\n"
        f"  zenodo_metadata.json paste into the Zenodo form, or use the API\n"
        f"\nReview {out} before uploading. A published Zenodo DOI cannot be "
        f"withdrawn.\n"
        f"After publishing, record the DOI in README.md and data/README.md."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
