#!/usr/bin/env python
"""Verify (or regenerate) the checksum manifest for committed processed data.

The paper figures read only ``data/processed``. This script proves that tree
is intact and unmodified, which is the cheapest possible reproducibility
check for someone who has just cloned the repo.

Usage
-----
Verify the working tree against the committed manifest::

    python scripts/verify_data.py

Regenerate the manifest after intentionally adding or updating data::

    python scripts/verify_data.py --write

Also report on the large upstream dataset, if it is reachable::

    python scripts/verify_data.py --check-upstream

Exit status is 0 when everything matches, 1 on any mismatch, missing or
unexpected file -- so this is usable as a CI step or a pre-submission gate.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data" / "processed"
MANIFEST = REPO / "data" / "MANIFEST.sha256"

# Written by the analysis but not part of the committed tier.
IGNORE_NAMES = {".DS_Store", "Thumbs.db"}


def sha256(path: Path, chunk: int = 1 << 20) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(chunk), b""):
            digest.update(block)
    return digest.hexdigest()


def iter_data_files() -> list[Path]:
    if not DATA.is_dir():
        return []
    return sorted(
        p for p in DATA.rglob("*")
        if p.is_file() and p.name not in IGNORE_NAMES
    )


def rel(path: Path) -> str:
    # Forward slashes so the manifest is identical on Windows and macOS.
    return path.relative_to(REPO).as_posix()


def write_manifest() -> int:
    files = iter_data_files()
    if not files:
        print(f"error: no files found under {DATA}", file=sys.stderr)
        return 1

    lines = [
        "# SHA-256 manifest for data/processed -- the post-hoc processed data",
        "# the paper figures are generated from.",
        "#",
        "# Regenerate with:  python scripts/verify_data.py --write",
        "# Verify with:      python scripts/verify_data.py",
        "#",
        "# <sha256>  <size_bytes>  <path>",
    ]
    total = 0
    for path in files:
        size = path.stat().st_size
        total += size
        lines.append(f"{sha256(path)}  {size}  {rel(path)}")

    lines.append(
        f"# {len(files)} files, {total} bytes ({total / 1024 / 1024:.1f} MiB)"
    )
    MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {rel(MANIFEST)}: {len(files)} files, {total / 1024 / 1024:.1f} MiB")
    return 0


def parse_manifest() -> dict[str, tuple[str, int]]:
    entries: dict[str, tuple[str, int]] = {}
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 2)
        if len(parts) != 3:
            continue
        digest, size, path = parts
        entries[path] = (digest, int(size))
    return entries


def verify() -> int:
    if not MANIFEST.is_file():
        print(
            f"error: {rel(MANIFEST)} not found.\n"
            "Generate it with: python scripts/verify_data.py --write",
            file=sys.stderr,
        )
        return 1

    expected = parse_manifest()
    actual = {rel(p): p for p in iter_data_files()}

    missing = sorted(set(expected) - set(actual))
    extra = sorted(set(actual) - set(expected))
    changed: list[str] = []

    for path in sorted(set(expected) & set(actual)):
        want_digest, want_size = expected[path]
        real = actual[path]
        if real.stat().st_size != want_size or sha256(real) != want_digest:
            changed.append(path)

    for path in missing:
        print(f"MISSING   {path}")
    for path in changed:
        print(f"CHANGED   {path}")
    for path in extra:
        print(f"UNTRACKED {path}")

    ok = len(expected) - len(missing) - len(changed)
    print(
        f"\n{ok}/{len(expected)} files verified"
        f" | {len(missing)} missing, {len(changed)} changed, {len(extra)} untracked"
    )

    if missing or changed:
        print(
            "\ndata/processed does not match the manifest. If you changed it on "
            "purpose, re-run with --write and commit the new manifest.",
            file=sys.stderr,
        )
        return 1
    if extra:
        print(
            "\nNew files are present but not in the manifest. Add them with "
            "--write if they belong in the committed tier.",
            file=sys.stderr,
        )
        return 1
    print("data/processed is intact.")
    return 0


def check_upstream() -> int:
    """Report whether the large, non-committed upstream dataset is reachable."""
    sys.path.insert(0, str(REPO))
    try:
        from onep import paths
    except ImportError as exc:
        print(f"could not import onep ({exc}); run `pip install -e .`", file=sys.stderr)
        return 1

    root = paths.data_root(required=False)
    if root is None:
        print(
            "upstream dataset: NOT FOUND (optional).\n"
            "  The paper figures do not need it. It is only required to "
            "regenerate data/processed from raw traces.\n"
            "  See data/README.md to configure DCA1_DATA_ROOT."
        )
        return 0

    print(f"upstream dataset: {root}")
    status = 0
    for session in ("hab", "fc", "cxta", "cxtb"):
        target = paths.collection(session, required=False)
        if target.exists():
            size = target.stat().st_size / 1024 / 1024
            print(f"  OK      collection_{session}_allmice.pkl  ({size:.0f} MiB)")
        else:
            print(f"  MISSING {target}")
            status = 1
    traces_dir = root / "Cell_Traces"
    print(
        f"  {'OK     ' if traces_dir.is_dir() else 'MISSING'} Cell_Traces/"
    )
    return status


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "--write", action="store_true",
        help="regenerate data/MANIFEST.sha256 from the current tree",
    )
    parser.add_argument(
        "--check-upstream", action="store_true",
        help="also report on the large non-committed dataset",
    )
    args = parser.parse_args()

    if args.write:
        return write_manifest()

    status = verify()
    if args.check_upstream:
        print()
        status |= check_upstream()
    return status


if __name__ == "__main__":
    raise SystemExit(main())
