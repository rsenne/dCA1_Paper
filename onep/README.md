# `onep` — one-photon analysis package

Installable package backing every notebook and script in this repo.

```bash
pip install -e .        # from the repo root
```

```python
import onep as op                              # re-exports the analysis API
from onep import paths                         # path resolution
from onep.cell_registration import CellReg     # submodules
```

## Modules

| Module | Contents |
|---|---|
| [paths.py](paths.py) | Machine-independent resolution of data and figure locations. Start here. |
| [onephoton.py](onephoton.py) | `InscopixProcessing`, `dCA1Group` — trace loading, ΔF/F, detrending, event detection, session collections |
| [trace_analysis_functions.py](trace_analysis_functions.py) | Event-triggered averages, cross-validated sequence heatmaps, ρ statistics |
| [behavior_analysis.py](behavior_analysis.py) | AnyMaze freezing parsing, freeze-vector alignment to imaging frames, Kalman-smoothed velocity |
| [cell_registration.py](cell_registration.py) | `CellReg` — CellReg output loading, affine FOV alignment, footprint overlays. See [../docs/cell_registration_pipeline.md](../docs/cell_registration_pipeline.md) |

`__init__.py` star-imports the first four, so `import onep as op` gives the flat
API the notebooks use. `cell_registration` is imported explicitly because it
pulls in optional GUI dependencies (`pip install -e ".[cellreg]"`).

## Layout notes

This package is deliberately **flat**. It previously nested modules under
`onep/Finalized/` and `onep/Old_Analyses/` — folders named after workflow
status rather than function — which meant importable library code lived in a
directory called "Old_Analyses" and imports like
`from onep.Finalized.trace_analysis_functions import ...` leaked authorship
history into the API. Those three modules were promoted to the package root in
the 2026 reorganisation.

## Adding code

- **Never hardcode a path.** Use `paths.processed()`, `paths.collection()`,
  `paths.figure_path()`. Add new mount points to `_KNOWN_DATA_ROOTS` in
  [paths.py](paths.py) or to your local `config.ini` — not to analysis code.
- Keep heavyweight or fragile imports (`holoviews`, `pymc`, `umap`, `cv2`)
  inside the module that needs them and declare them as an extra in
  [../pyproject.toml](../pyproject.toml), so the base install stays light.
