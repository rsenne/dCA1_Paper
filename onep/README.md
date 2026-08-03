# `onep`

```bash
pip install -e .        # from the repo root
```

```python
import onep as op                              # flat API used by the notebooks
from onep import paths                         # path resolution
from onep.cell_registration import CellReg     # optional GUI deps
```

| Module | Contents |
|---|---|
| `paths.py` | resolves data and figure locations per machine |
| `onephoton.py` | `InscopixProcessing`, `dCA1Group`  trace loading, ΔF/F, detrending, event detection |
| `trace_analysis_functions.py` | event-triggered averages, cross-validated sequence heatmaps, ρ stats |
| `behavior_analysis.py` | AnyMaze freezing parsing, freeze-vector alignment, Kalman-smoothed velocity |
| `cell_registration.py` | CellReg output loading, affine FOV alignment, footprint overlays |

`__init__.py` star-imports the first four so `import onep as op` gives
everything the notebooks use. `cell_registration` stays separate because it
pulls in holoviews/bokeh/panel (`pip install -e ".[cellreg]"`).

The package is flat. Three of these modules previously sat under
`onep/Finalized/` and `onep/Old_Analyses/`, which meant imported library code
lived in a folder called "Old_Analyses" and import paths encoded who wrote
what.

When adding code, use `paths.processed()` / `paths.collection()` /
`paths.figure_path()` rather than literal paths, and add new mount points to
`_KNOWN_DATA_ROOTS` in `paths.py` or to your local `config.ini`. Keep fragile
imports (holoviews, pymc, umap, cv2) inside the module that needs them and
declare them as an extra in `../pyproject.toml`.
