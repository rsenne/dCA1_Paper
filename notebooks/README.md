# Notebooks

Organised by **role**, not by author. The figure map with per-notebook data
dependencies is in the [root README](../README.md#figure-map).

| Folder | Purpose | Needs tier-2 data? |
|---|---|---|
| [figures/](figures/) | Main paper figures (Fig 1–4) | Mostly no |
| [supplementary/](supplementary/) | Supplemental figures and statistics | Some |
| [preprocessing/](preprocessing/) | Rebuilding processed data from raw imaging | Yes |

## Before you run anything

```bash
pip install -e .              # from the repo root
python -m onep.paths          # confirm data + output locations resolve
```

## Conventions

Notebooks read and write through [`onep.paths`](../onep/paths.py). There are no
absolute paths anywhere in this tree, and nothing writes to a Desktop.

```python
import pandas as pd
from onep import paths

df = pd.read_csv(paths.processed("figure3", "Num_Detected_Events.csv"))

fig.savefig(paths.figure_path("figure3", "num_events.svg"))   # -> results/figures/figure3/
```

Useful helpers:

| Call | Returns |
|---|---|
| `paths.processed(*parts)` | File in `data/processed`, erroring with a directory listing if absent |
| `paths.collection(session)` | Tier-2 pickle for `hab` / `fc` / `cxta` / `cxtb` |
| `paths.traces(animal, session)` | Tier-2 per-animal trace CSV |
| `paths.figure_path(*parts)` | Output path under `results/figures`, parent dirs created |
| `paths.data_root(required=False)` | Tier-2 root, or `None` — for graceful degradation |

Notebooks that need tier-2 data should fail with a clear message rather than a
`FileNotFoundError` deep inside pandas:

```python
if paths.data_root(required=False) is None:
    raise RuntimeError(
        "This notebook needs the upstream dataset; see data/README.md. "
        "The figure it produces is also reproducible from data/processed."
    )
```

## Outputs are kept

Executed outputs are intentionally committed for the notebooks in `figures/`
and `supplementary/`: they record what correct output looks like for a paper
repo. This does mean notebook diffs are noisy. If you want clean diffs locally:

```bash
pip install nbstripout      # included in the [dev] extra
nbstripout --install        # opt-in, per-clone; do not commit stripped figures
```

Notebooks under [../archive/](../archive/) have already had their outputs
stripped, since they are kept only for provenance.

## Execution order

`figures/` and `supplementary/` notebooks are independent — run them in any
order. `preprocessing/` is a pipeline; see the
[preprocessing section of the root README](../README.md#preprocessing-pipeline)
for the correct sequence.
