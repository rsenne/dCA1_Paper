"""Machine-independent path resolution for the dCA1 analysis code.

Historically every notebook in this repo hardcoded an absolute path to
whichever machine it was written on (``/Users/suthardr/Desktop/...``,
``Z:/Home/rsenne/...``, ``/Volumes/rkc_ramirezlab/...``). That made the
analyses impossible to re-run anywhere else. This module centralises the
three locations any analysis needs:

``processed_dir()``
    Post-hoc processed data that ships **inside** this repository
    (``data/processed``). Every paper figure can be regenerated from these
    files alone, so this always resolves with no configuration.

``data_root()``
    The large upstream dataset that is **not** in git -- pickled session
    collections (~460 MB) and raw Inscopix cell traces (~470 MB). Only
    needed to regenerate ``data/processed`` from scratch.

``figures_dir()``
    Where generated figures are written. Defaults to ``results/figures``
    inside the repo, so notebooks never write to somebody's Desktop.

Configuration is resolved in this order, first hit wins:

1. Environment variable (``DCA1_DATA_ROOT`` / ``DCA1_FIGURE_DIR``).
2. A ``config.ini`` in the repository root (see ``config.example.ini``).
3. Known lab mount points, so existing collaborators need no setup.

Examples
--------
>>> from onep import paths
>>> paths.processed_dir()                      # doctest: +SKIP
WindowsPath('.../dCA1_Paper/data/processed')
>>> paths.processed("figure2", "crossval_summary_results.csv")   # doctest: +SKIP
WindowsPath('.../data/processed/figure2/crossval_summary_results.csv')
>>> paths.collection("fc")                     # doctest: +SKIP
WindowsPath('Z:/Home/rsenne/dCA1_Clean_Data/Dill/collection_fc_allmice.pkl')
"""

from __future__ import annotations

import configparser
import os
from pathlib import Path

__all__ = [
    "repo_root",
    "processed_dir",
    "processed",
    "data_root",
    "resolve",
    "collection",
    "traces",
    "intermediates",
    "intermediate",
    "figures_dir",
    "figure_path",
    "describe",
]

# Mount points where the upstream dataset is known to live, tried in order.
# Add your own rather than editing analysis code.
_KNOWN_DATA_ROOTS = (
    # Mapped drive letter (Windows). Convenient but often shows as
    # "Unavailable" after a reboot or off-VPN, so the UNC path below is tried
    # next -- it works whenever the share is reachable, mapped or not.
    "Z:/Home/rsenne/dCA1_Clean_Data",
    r"\\nas1.bu.edu\rkc_ramirezlab\Home\rsenne\dCA1_Clean_Data",
    "//nas1.bu.edu/rkc_ramirezlab/Home/rsenne/dCA1_Clean_Data",
    # macOS mounts of the same share.
    "/Volumes/rkc_ramirezlab/Home/rsenne/dCA1_Clean_Data",
    "/Volumes/rsenne/dCA1_Clean_Data",
)

_CONFIG_NAME = "config.ini"
_SESSIONS = ("hab", "fc", "cxta", "cxtb")


def repo_root() -> Path:
    """Absolute path to the repository root (the parent of ``onep/``)."""
    return Path(__file__).resolve().parent.parent


def _config() -> configparser.ConfigParser:
    cfg = configparser.ConfigParser()
    candidate = repo_root() / _CONFIG_NAME
    if candidate.is_file():
        cfg.read(candidate)
    return cfg


def _from_config(key: str) -> str | None:
    cfg = _config()
    if cfg.has_option("paths", key):
        value = cfg.get("paths", key).strip()
        return value or None
    return None


# --------------------------------------------------------------------------
# In-repo processed data
# --------------------------------------------------------------------------

def processed_dir() -> Path:
    """Directory of post-hoc processed data committed to this repo.

    This is the tier of data the paper figures actually read, so it always
    resolves without configuration.
    """
    return repo_root() / "data" / "processed"


def processed(*parts: str) -> Path:
    """Resolve a path under :func:`processed_dir`, checking that it exists.

    Raises
    ------
    FileNotFoundError
        If the file is missing, listing what *is* present in the target
        directory -- usually a renamed or misremembered filename.
    """
    target = processed_dir().joinpath(*parts)
    if not target.exists():
        parent = target.parent
        if parent.is_dir():
            available = sorted(p.name for p in parent.iterdir())
            hint = "\n  ".join(available) or "(directory is empty)"
            raise FileNotFoundError(
                f"{target} does not exist.\nAvailable in {parent}:\n  {hint}"
            )
        raise FileNotFoundError(
            f"{target} does not exist (directory {parent} is missing). "
            "Is this a complete clone of the repository?"
        )
    return target


# --------------------------------------------------------------------------
# External upstream data
# --------------------------------------------------------------------------

def data_root(required: bool = True) -> Path | None:
    """Locate the large upstream dataset that is not tracked in git.

    Parameters
    ----------
    required
        When ``True`` (default) raise if the dataset cannot be found. Pass
        ``False`` to get ``None`` instead, for notebooks that can fall back
        to the processed data in the repo.

    Raises
    ------
    FileNotFoundError
        With setup instructions, if no candidate location exists.
    """
    candidates: list[str] = []

    env = os.environ.get("DCA1_DATA_ROOT")
    if env:
        candidates.append(env)

    configured = _from_config("data_root")
    if configured:
        candidates.append(configured)

    candidates.extend(_KNOWN_DATA_ROOTS)

    for candidate in candidates:
        path = Path(candidate).expanduser()
        if path.is_dir():
            return path

    if not required:
        return None

    tried = "\n  ".join(candidates)
    raise FileNotFoundError(
        "Could not locate the upstream dCA1 dataset.\n"
        "This is only needed to regenerate data/processed from raw traces; "
        "the paper figures run from data/processed alone.\n\n"
        "Set it one of these ways:\n"
        "  1. export DCA1_DATA_ROOT=/path/to/dCA1_Clean_Data\n"
        f"  2. copy config.example.ini to {repo_root() / _CONFIG_NAME} "
        "and set data_root\n\n"
        f"Locations tried:\n  {tried}\n\n"
        "See data/README.md for how to obtain the dataset."
    )


def resolve(*parts: str, required: bool = True) -> Path:
    """Resolve a path under :func:`data_root`.

    With ``required=True`` the file must exist; the error names the missing
    file rather than failing later inside pandas.
    """
    target = data_root().joinpath(*parts)
    if required and not target.exists():
        raise FileNotFoundError(
            f"{target} does not exist under the configured data root. "
            "See data/README.md for the expected layout."
        )
    return target


def collection(session: str, required: bool = True) -> Path:
    """Path to a pickled all-mice session collection.

    Parameters
    ----------
    session
        One of ``hab``, ``fc``, ``cxta``, ``cxtb``.
    """
    key = session.lower()
    if key not in _SESSIONS:
        raise ValueError(
            f"Unknown session {session!r}; expected one of {', '.join(_SESSIONS)}"
        )
    return resolve("Dill", f"collection_{key}_allmice.pkl", required=required)


def traces(animal: str, session: str, required: bool = True) -> Path:
    """Path to one animal's Inscopix trace CSV for a given session."""
    return resolve(
        "Cell_Traces", f"{animal}_traces", f"{animal}_{session}_traces.csv",
        required=required,
    )


# --------------------------------------------------------------------------
# Derived intermediates
# --------------------------------------------------------------------------

# Candidate locations for the derived trace-export tree, tried in order.
_KNOWN_INTERMEDIATE_ROOTS = (
    "C:/Users/ryansenne/Desktop/Dill",
    "~/Desktop/Dill",
)

# A valid intermediates root contains at least one of these.
_INTERMEDIATE_MARKERS = ("fc_traces_csv", "cxta_traces_csv", "cxtb_traces_csv",
                         "hab_traces_csv")


def _looks_like_intermediates(path: Path) -> bool:
    return path.is_dir() and any((path / m).is_dir() for m in _INTERMEDIATE_MARKERS)


def intermediates(required: bool = True) -> Path | None:
    """Locate the derived trace-export tree.

    This is a fourth location, distinct from :func:`data_root`: per-animal
    ``*_accepted_traces.csv``, ``time.csv``, ``event_times.csv`` and
    ``freeze_vec_cxt_*.csv`` files, grouped into ``{session}_traces_csv/``
    directories, plus DeepLabCut output under ``dlc/``.

    They are produced by ``scripts/Export_Files_Rui.py`` and the Julia
    sequence detector, so they are regenerable and not committed. Several
    supplementary notebooks read them.

    Resolution order: ``DCA1_INTERMEDIATES`` environment variable,
    ``intermediates`` in ``config.ini``, then known locations. A candidate
    only counts if it actually contains a ``*_traces_csv`` directory, so a
    stale setting is reported rather than silently used.
    """
    candidates: list[str] = []

    env = os.environ.get("DCA1_INTERMEDIATES")
    if env:
        candidates.append(env)

    configured = _from_config("intermediates")
    if configured:
        candidates.append(configured)

    candidates.extend(_KNOWN_INTERMEDIATE_ROOTS)

    # The Zenodo deposit extracts to <data_root>/Derived_Exports.
    root = data_root(required=False)
    if root is not None:
        candidates.append(str(root / "Derived_Exports"))

    for candidate in candidates:
        path = Path(candidate).expanduser()
        if _looks_like_intermediates(path):
            return path

    if not required:
        return None

    tried = "\n  ".join(candidates) or "(none)"
    raise FileNotFoundError(
        "Could not locate the derived trace exports.\n"
        "These are needed by the sequence, cosine-similarity, freezing and\n"
        "habituation supplementary notebooks. They are not required for any\n"
        "main figure.\n\n"
        "Either regenerate them:\n"
        "  python scripts/Export_Files_Rui.py --session fc   (and cxta/cxtb/hab)\n"
        "then run the Julia detector in julia/ for the event times; or download\n"
        "dca1_derived_intermediates.zip from the Zenodo deposit and set:\n"
        "  export DCA1_INTERMEDIATES=/path/to/extracted\n\n"
        f"Locations tried:\n  {tried}\n\n"
        "A directory only counts if it contains a *_traces_csv subdirectory."
    )


def intermediate(*parts: str, required: bool = True) -> Path:
    """Resolve a path under :func:`intermediates`."""
    target = intermediates().joinpath(*parts)
    if required and not target.exists():
        parent = target.parent
        if parent.is_dir():
            available = sorted(p.name for p in parent.iterdir())[:20]
            hint = "\n  ".join(available) or "(empty)"
            raise FileNotFoundError(
                f"{target} does not exist.\nPresent in {parent}:\n  {hint}"
            )
        raise FileNotFoundError(f"{target} does not exist ({parent} is missing).")
    return target


# --------------------------------------------------------------------------
# Figure output
# --------------------------------------------------------------------------

def figures_dir(*parts: str) -> Path:
    """Directory for generated figures, created if absent.

    Defaults to ``results/figures`` in the repo. Override with the
    ``DCA1_FIGURE_DIR`` environment variable or ``figure_dir`` in
    ``config.ini``. ``results/`` is gitignored, so re-running notebooks
    never dirties the working tree.
    """
    base = os.environ.get("DCA1_FIGURE_DIR") or _from_config("figure_dir")
    root = Path(base).expanduser() if base else repo_root() / "results" / "figures"
    target = root.joinpath(*parts)
    target.mkdir(parents=True, exist_ok=True)
    return target


def figure_path(*parts: str) -> Path:
    """Full path for a figure file, creating its parent directory.

    >>> figure_path("figure2", "shock_eta.svg")   # doctest: +SKIP
    WindowsPath('.../results/figures/figure2/shock_eta.svg')
    """
    if not parts:
        raise ValueError("figure_path() needs at least a filename")
    *subdirs, filename = parts
    return figures_dir(*subdirs) / filename


def describe() -> str:
    """Human-readable summary of resolved paths, for notebook sanity checks."""
    found = data_root(required=False)
    inter = intermediates(required=False)
    lines = [
        f"repo root      : {repo_root()}",
        f"processed data : {processed_dir()}"
        f"{'' if processed_dir().is_dir() else '   [MISSING]'}",
        f"figure output  : {figures_dir()}",
        f"imaging data   : {found if found else '[not found - needed for some figures]'}",
        f"intermediates  : {inter if inter else '[not found - needed for 6 supplementals]'}",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    print(describe())
