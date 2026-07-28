# dCA1 Astrocyte Paper — Analysis Code

Analysis code and processed data for the dorsal CA1 astrocyte calcium imaging
study: one-photon (Inscopix) imaging of dCA1 astrocytes across habituation,
contextual fear conditioning (FC), and two recall contexts (CxtA, CxtB).

> **Paper:** _A hippocampal astrocytic sequence emerges during learning and memory_
>
> <!-- TODO: add authors, journal, and DOI once accepted -->
> **Citation:** _authors, journal, DOI — to be added on acceptance_

---

## Quick start

```bash
git clone <this repo> && cd dCA1_Paper
pip install -r requirements.txt        # installs the `onep` package + deps
python scripts/verify_data.py          # confirms the committed data is intact
jupyter lab notebooks/figures/
```

That is enough to regenerate **every figure panel in the paper**. The
committed data in [data/processed/](data/processed/) (26 MB) is all the figure
notebooks read. You do **not** need the lab share or any raw imaging data
unless you want to rebuild that processed tier from scratch.

Figures are written to `results/figures/` (gitignored), never to your Desktop.

---

## Repository layout

| Path | Contents |
|---|---|
| [onep/](onep/) | The importable analysis package — trace processing, cell registration, behaviour, and path resolution |
| [notebooks/figures/](notebooks/figures/) | Main paper figures (Fig 1–4) |
| [notebooks/supplementary/](notebooks/supplementary/) | Supplemental figures and statistics |
| [notebooks/preprocessing/](notebooks/preprocessing/) | Upstream pipeline: cell registration, session collections, WaveMAP arrays |
| [data/processed/](data/processed/) | Post-hoc processed data the figures read (tracked in git) |
| [scripts/](scripts/) | Standalone entry points: data export, trace movies, verification |
| [julia/](julia/) | Julia/Pluto sequence-detection model |
| [docs/](docs/) | Pipeline documentation |
| [archive/](archive/) | Superseded analyses, kept for provenance — **not** part of the paper pipeline |

---

## Reproducing the figures

Each notebook is self-contained and reads only from `data/processed`. Every
path goes through [`onep.paths`](onep/paths.py), so nothing is machine-specific.

```python
from onep import paths

df = pd.read_csv(paths.processed("figure2", "crossval_summary_results.csv"))
fig.savefig(paths.figure_path("figure2", "crossval_rho.svg"))
```

Sanity-check your setup at any time:

```bash
python -m onep.paths          # prints every resolved location
```

### Figure map

Mapping is given with the **evidence** — the processed file each notebook
reads — so you can verify it rather than take it on faith.

#### Main figures

| Notebook | Reads | Produces |
|---|---|---|
| [Fig1_total_cells_and_reactivated](notebooks/figures/Fig1_total_cells_and_reactivated.ipynb) | `figure1/Normalized_UniqueCells_FC_Pair.csv`, `registration_counts_{wide,long}.csv` | Cells registered & reactivated across session pairs (by order, by sex) |
| [Fig2_shockETA](notebooks/figures/Fig2_shockETA.ipynb) | `collection_fc_allmice.pkl` (tier 2) | Shock event-triggered average; peak distribution by sex |
| [Fig2_Shock_responsive_inset](notebooks/figures/Fig2_Shock_responsive_inset.ipynb) | `collection_fc_allmice.pkl` (tier 2) | Shock-responsive proportion pie chart |
| [Fig2_crossvalled_heatmaps_rho_regression_FC](notebooks/figures/Fig2_crossvalled_heatmaps_rho_regression_FC.ipynb) | `figure2/crossval_summary_results.csv` | Cross-validated FC sequence heatmaps, paired ρ, shuffle null |
| [Figure2_3_distribution_histograms](notebooks/figures/Figure2_3_distribution_histograms.ipynb) | `modeling/astrocyte_*_Gaussian_noise3_all.csv` | Predicted-peak-time histograms (FC, CxtA, CxtB) |
| [Fig3_NumDetectedEvents](notebooks/figures/Fig3_NumDetectedEvents.ipynb) | `figure3/Num_Detected_Events.csv` | Number of detected events by context and sex |
| [Figure3_Cross_valled](notebooks/figures/Figure3_Cross_valled.ipynb) | `figure3/crossval_summary_results_cxt{a,b}.csv`, `event_times_cxt{a,b}.csv` | Recall cross-validated ρ vs shuffle, Δρ |
| [Fig4_Crossvalled_Heatmaps](notebooks/figures/Fig4_Crossvalled_Heatmaps.ipynb) | `figure4/FC_crossval_reactivation_summary_CxtA_CxtB.csv`, `Fig4_FCvsRecall_shuffle_summary.csv` | Reactivated-cell sequence reinstatement, FC vs recall shuffle |

#### Supplemental

| Notebook | Reads | Corresponds to |
|---|---|---|
| [Supp_IHC](notebooks/supplementary/Supp_IHC.ipynb) | `supplementary/ihc/IHC_Counts.csv` | IHC specificity (Supp 1) |
| [behavior_plots](notebooks/supplementary/behavior_plots.ipynb) | `behavior/{hab,fc,cxta,cxtb}_freezing.csv` | Freezing by group / order / sex (Supp 2) |
| [Cosine_Similarity](notebooks/supplementary/Cosine_Similarity.ipynb) | `figure3/event_times_cxt{a,b}.csv` + tier-2 traces | Cosine-similarity matrices, FC / CxtA / CxtB (Supp 3, 9, 10) |
| [PreShockAnalysis](notebooks/supplementary/PreShockAnalysis.ipynb) | tier-2 collections + DLC velocity | Movement / velocity analysis (Supp 4) |
| [Supp_1stv2ndHalf](notebooks/supplementary/Supp_1stv2ndHalf.ipynb) | `supplementary/first_v_second/crossval_summary_results.csv` | First vs second half FC cross-validation (Supp 6) |
| [Supp_WaveMap](notebooks/supplementary/Supp_WaveMap.ipynb) | `supplementary/wavemap/*` | WaveMAP UMAP clustering of shock responses (Supp 8) |
| [Seq_Detector](notebooks/supplementary/Seq_Detector.ipynb), [theoretical_dists](notebooks/supplementary/theoretical_dists.ipynb) | tier-2 traces | Sequence-detector validation (Supp 11) |
| [Freezing_Seqs_Analysis](notebooks/supplementary/Freezing_Seqs_Analysis.ipynb) | tier-2 freeze vectors | Sequence–freezing relationship, CxtA / CxtB (Supp 12, 13) |
| [Hab_Figure](notebooks/supplementary/Hab_Figure.ipynb) | `collection_hab_allmice.pkl` (tier 2) | Habituation session (Supp 19) |
| [Figure_2_peak_props](notebooks/supplementary/Figure_2_peak_props.ipynb) | `modeling/astrocyte_shot_Gaussian_noise3_all.csv` | Linear mixed-effects model of peak properties |
| [Sequence_variance_plots](notebooks/supplementary/Sequence_variance_plots.ipynb) | `modeling/astrocyte_*_Gaussian_noise3_all.csv` | Per-cell peak variance across FC / A / B |
| [Freezing_Analysis](notebooks/supplementary/Freezing_Analysis.ipynb) | `behavior/*_freezing.csv` | Freezing metrics and activity–freezing vectors |

Supplemental numbering follows the round-1 revision figure set; notebooks whose
"Reads" column names a tier-2 file need the upstream dataset (see below).

---

## Data

Three tiers, only the first of which is in git:

| Tier | What | Size | Location |
|---|---|---|---|
| **1. Processed** | Per-figure summary tables, UMAP embeddings, model outputs, freezing summaries | 26 MB | **In this repo**, [data/processed/](data/processed/) |
| **2. Upstream** | Pickled session collections (`collection_*_allmice.pkl`), raw Inscopix cell traces | ~940 MB | Lab share / archive |
| **3. Raw** | Inscopix `.isxd` movies, CellReg outputs, behaviour video | Many GB | Lab share only |

Integrity of tier 1 is guaranteed by a checksum manifest:

```bash
python scripts/verify_data.py                    # verify tier 1
python scripts/verify_data.py --check-upstream   # also report on tier 2
```

To work with tier 2, point the code at it — no source edits required:

```bash
export DCA1_DATA_ROOT=/path/to/dCA1_Clean_Data
# or: cp config.example.ini config.ini  and set data_root
```

Known lab mounts (`Z:/Home/rsenne/...`, `/Volumes/rkc_ramirezlab/Home/rsenne/...`)
are auto-detected, so collaborators on the share need no configuration.

See [data/README.md](data/README.md) for per-file provenance.

---

## Installation notes

The base install covers the figure notebooks. Heavier, more fragile
dependencies are optional extras:

```bash
pip install -e .              # figures + stats
pip install -e ".[cellreg]"   # cell registration GUI (holoviews, bokeh, panel)
pip install -e ".[bayes]"     # PyMC hierarchical models
pip install -e ".[wavemap]"   # UMAP / Louvain clustering
pip install -e ".[video]"     # trace + behaviour movie rendering
pip install -e ".[all]"       # everything (same as requirements.txt)
```

Conda users: `conda env create -f environment.yml`.

Python ≥ 3.10. Version constraints live in [pyproject.toml](pyproject.toml),
which is the single source of truth — `requirements.txt` just points at it.

---

## Preprocessing pipeline

Only needed to rebuild tier 1 from raw data. Run in order:

1. **Cell registration** — see [docs/cell_registration_pipeline.md](docs/cell_registration_pipeline.md)
   for the IDPS export steps and folder layout, then
   [affine_transform](notebooks/preprocessing/affine_transform.ipynb) (FOV alignment) →
   CellReg (MATLAB) → [eval_cellreg_rebecca](notebooks/preprocessing/eval_cellreg_rebecca.ipynb) (manual QC).
2. **Session collections** — [Save_Collections](notebooks/preprocessing/Save_Collections.ipynb)
   builds the `collection_{session}_allmice.pkl` files (tier 2) from cell traces.
3. **WaveMAP arrays** — [Create_WaveMAP_numpy_arrays_CFC_Recall](notebooks/preprocessing/Create_WaveMAP_numpy_arrays_CFC_Recall.ipynb)
   produces `shock_epoch_cells_x_time_z.npy`, consumed by the WaveMAP supplement.
4. **Sequence detection** — the Julia/Pluto model in [julia/](julia/).

---

## Repository conventions

- **No absolute paths in analysis code.** Use `onep.paths`. The pre-2026 code
  hardcoded per-machine Desktop paths, which is what made the analyses
  unreproducible; please don't reintroduce it.
- **Figures go to `results/`**, which is gitignored.
- **`data/processed` is byte-exact.** It is marked `-text` in
  [.gitattributes](.gitattributes) so line-ending normalisation cannot alter
  data or invalidate checksums. If you change it deliberately, re-run
  `python scripts/verify_data.py --write` and commit the new manifest.
- **Do not add a blanket `*.csv` to `.gitignore`.** That rule previously kept
  every result table out of the repository.
