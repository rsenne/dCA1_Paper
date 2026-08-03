# A hippocampal astrocytic sequence emerges during learning and memory

Analysis code for one-photon calcium imaging of dorsal CA1 astrocytes across
habituation, contextual fear conditioning, and two recall contexts (A and B).

Senne, Suthard, Monasterio et al. *In revision.*
<!-- add journal + DOI on acceptance -->

## Setup

```bash
git clone https://github.com/rsenne/dCA1_Paper && cd dCA1_Paper
python -m venv .venv && source .venv/Scripts/activate   # or bin/activate on macOS
pip install -r requirements.txt
python scripts/verify_data.py
```

Then open `notebooks/figures/`. Seven notebooks run on the data in this repo with
no further setup; the rest need the imaging dataset (see [Data](#data)).

Figures are written to `results/figures/`, which is gitignored.

## Layout

```
onep/                  analysis package (traces, behaviour, cell registration, paths)
notebooks/figures/     main figures
notebooks/supplementary/  supplemental figures and stats
notebooks/preprocessing/  cell registration, session collections, WaveMAP arrays
data/processed/        26 MB of processed tables the figures read (tracked)
scripts/               data export, trace movies, verification
julia/                 Pluto notebook for the HMM sequence detector
docs/                  cell registration pipeline
archive/               superseded analyses, kept for provenance
```

## Data

Three tiers. Only the first is in git.

| Tier | Contents | Size | Where |
|---|---|---|---|
| Processed | per-figure summary tables, UMAP embeddings, model output | 26 MB | `data/processed/` (42 files) |
| Imaging | session collections (`*.pkl`), Inscopix cell traces | ~940 MB | lab share |
| Raw | `.isxd` movies, CellReg output, behaviour video | tens of GB | lab share |

`data/processed` has a checksum manifest:

```bash
python scripts/verify_data.py                   # verify the 42 committed files
python scripts/verify_data.py --check-upstream   # also look for the imaging tier
```

To use the imaging tier, point the code at it — no source edits:

```bash
export DCA1_DATA_ROOT=/path/to/dCA1_Clean_Data
```

or copy `config.example.ini` to `config.ini` and set `data_root`. The Ramirez
lab mounts are detected automatically, including the `\nas1.bu.edu` UNC path,
which keeps working when the `Z:` mapping drops off VPN.

Per-file provenance is in [data/README.md](data/README.md).

## Paths

Notebooks resolve every path through `onep.paths`, so they run unchanged on any
machine:

```python
from onep import paths

pd.read_csv(paths.processed("figure3", "Num_Detected_Events.csv"))
pickle.load(open(paths.collection("fc"), "rb"))
fig.savefig(paths.figure_path("figure3", "num_events.svg"))
```

`python -m onep.paths` prints what resolves on your machine.

## Figures

"Data" is the tier a notebook needs. "Verified" means it was executed
top-to-bottom in a fresh kernel on 2026-07-31 against the pinned dependencies
and completed without error.

### Main

| Notebook | Data | Verified | Output |
|---|---|---|---|
| `Fig1_total_cells_and_reactivated` | processed | yes | cells registered and reactivated across session pairs |
| `Fig2_shockETA` | imaging | yes | shock event-triggered average, peak distribution by sex |
| `Fig2_Shock_responsive_inset` | imaging | yes | shock-responsive proportion |
| `Fig2_crossvalled_heatmaps_rho_regression_FC` | imaging | yes | cross-validated FC sequence heatmaps, paired ρ vs shuffle |
| `Figure2_3_distribution_histograms` | processed | yes | predicted peak-time distributions (FC, A, B) |
| `Fig3_NumDetectedEvents` | processed | yes | detected event counts by context and sex |
| `Figure3_Cross_valled` | imaging | yes | recall cross-validated ρ, Δρ between contexts |
| `Fig4_Crossvalled_Heatmaps` | imaging | yes | reactivated-cell sequence reinstatement, FC vs recall |

### Supplemental

| Notebook | Data | Verified | Output |
|---|---|---|---|
| `Supp_IHC` | processed | yes | viral specificity counts |
| `behavior_plots` | raw | yes | freezing by group, order, sex; writes the binned freezing tables |
| `Supp_1stv2ndHalf` | imaging | yes | FC cross-validation, first vs second half |
| `Supp_WaveMap` | processed + imaging | yes | UMAP clustering of shock responses |
| `Sequence_variance_plots` | processed | yes | per-cell peak variability across FC/A/B |
| `Figure_2_peak_props` | processed | yes | mixed-effects model of peak properties |
| `theoretical_dists` | none | yes | sequence detector validation (simulated) |
| `Cosine_Similarity` | intermediates | no | cosine similarity matrices per context |
| `PreShockAnalysis` | intermediates | no | velocity and movement controls |
| `Seq_Detector` | intermediates | no | sequence detector validation on real traces |
| `Freezing_Analysis`, `Freezing_Seqs_Analysis` | intermediates | no | freezing metrics, sequence–freezing relationship |
| `Hab_Figure` | intermediates | no | habituation session |

All eight main figures and six of the supplementals are verified: **14 notebooks
run clean, producing 228 figure files.**

**"no"** — these six still read from a personal working directory
(`C:\Users\ryansenne\Desktop\Dill`) that exists on one machine. They are not
broken, but they are not portable, so they have not been migrated to
`onep.paths` or run here.

They need a fourth data location the other tiers don't cover: derived trace
exports (`{animal}_{session}_accepted_traces.csv`, `time.csv`, `event_times.csv`,
`freeze_vec_cxt_{a,b}.csv`) produced by
[scripts/Export_Files_Rui.py](scripts/Export_Files_Rui.py) and the Julia
detector. That is ~360 MB of regenerable intermediates, so it belongs alongside
the imaging tier rather than in git, reached through a new
`paths.intermediates()` resolver. Migrating them is the main outstanding work;
[notebooks/README.md](notebooks/README.md) documents the procedure and the four
failure modes found while migrating the others.

## Preprocessing

Only needed to rebuild `data/processed` from raw imaging. In order:

1. Cell registration — [docs/cell_registration_pipeline.md](docs/cell_registration_pipeline.md)
   covers the IDPS exports and folder layout, then `affine_transform.ipynb`
   (FOV alignment), CellReg in MATLAB, `eval_cellreg_rebecca.ipynb` (QC).
2. `Save_Collections.ipynb` builds the per-session `collection_*.pkl` files.
3. `Create_WaveMAP_numpy_arrays_CFC_Recall.ipynb` builds the WaveMAP input array.
4. Sequence detection — the Pluto notebook in [julia/](julia/).

These notebooks have not been migrated to `onep.paths` either.

## Dependencies

Python ≥ 3.10. Constraints live in [pyproject.toml](pyproject.toml);
`requirements.txt` installs from it so the two cannot drift.

```bash
pip install -e .              # figures and stats
pip install -e ".[cellreg]"   # registration GUI (holoviews, bokeh, panel)
pip install -e ".[bayes]"     # PyMC models
pip install -e ".[wavemap]"   # UMAP, Louvain
pip install -e ".[video]"     # trace movie rendering
pip install -e ".[all]"
```

Conda: `conda env create -f environment.yml`.

## Notes

- Notebook outputs are committed for the figure notebooks, as a record of
  expected output. `pip install nbstripout && nbstripout --install` if you'd
  rather have clean diffs locally.
- `data/processed` is marked `-text` in `.gitattributes` so line-ending
  normalisation cannot alter the bytes or break the checksums. If you change it
  deliberately, re-run `verify_data.py --write` and commit the manifest.
- Don't add `*.csv` to `.gitignore` — an old blanket rule is why none of the
  result tables were tracked before.
