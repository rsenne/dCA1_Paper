# Archive

Superseded code kept for provenance. **Nothing here is part of the paper's
reproducible pipeline** — do not cite it, and expect it to be broken.

Outputs have been stripped from every notebook in this tree (10 MB → 0.2 MB),
so these files are cheap to keep but no longer show rendered figures. Their
imports were mechanically updated to the flattened `onep` package, but they
were **not** re-run or re-validated, and most still reference absolute paths on
machines that no longer exist.

## Contents

### `superseded_analyses/old_analyses/`

Earlier versions of analyses now in [../notebooks/](../notebooks/). Replaced by:

| Archived | Superseded by |
|---|---|
| `Fig4_Crossvalled_Reactivated.ipynb`, `Reactivated_Heatmaps.ipynb` | [Fig4_Crossvalled_Heatmaps](../notebooks/figures/Fig4_Crossvalled_Heatmaps.ipynb) |
| `Recall_heatmaps.ipynb`, `Recall_heatmaps_crossvalled_fig3.ipynb` | [Figure3_Cross_valled](../notebooks/figures/Figure3_Cross_valled.ipynb) |
| `Supplemental_WaveMAP.ipynb`, `WaveMAP_output_functions.ipynb`, `wavemap_posthoc_analysis.ipynb` | [Supp_WaveMap](../notebooks/supplementary/Supp_WaveMap.ipynb) |
| `Sequence_Detector.ipynb` | [Seq_Detector](../notebooks/supplementary/Seq_Detector.ipynb) |
| `heatmap_predmu.ipynb`, `pred_mu_vs_argmax_fc.ipynb` | [Figure2_3_distribution_histograms](../notebooks/figures/Figure2_3_distribution_histograms.ipynb) |
| `Figure1_plot_footprints.ipynb` | [plot_fig1_representative_fov.py](../scripts/plot_fig1_representative_fov.py) |
| `Time_analysis_2024.ipynb`, `Spearmans_Correlation.ipynb`, `evan_figure.ipynb`, `figure2.py`, `find_events.py`, `traces_umap.py`, `dlc_analysis.py`, `demo_filter_isx.py` | exploratory; no direct successor |

Four files that lived here were **not** superseded and were promoted out of the
archive during the reorganisation, because they are load-bearing:

- `cell_registration.py` → [../onep/cell_registration.py](../onep/cell_registration.py) (imported library code)
- `cell_registration README.md` → [../docs/cell_registration_pipeline.md](../docs/cell_registration_pipeline.md)
- `Create_WaveMAP_numpy_arrays_CFC_Recall.ipynb` → [../notebooks/preprocessing/](../notebooks/preprocessing/) (generates the WaveMAP input arrays)
- `eval_cellreg_rebecca.ipynb` → [../notebooks/preprocessing/](../notebooks/preprocessing/) (manual registration QC, step 7 of the pipeline)

### `superseded_analyses/amy_analyses/`

Exploratory filtering and smoothing work. `affine_transform.ipynb` and
`save_image_stacks.ipynb` were promoted to
[../notebooks/preprocessing/](../notebooks/preprocessing/) (steps 4–5 of the
cell registration pipeline), and `spatial_timemaps_supplemental.py`,
`figure1.py`, `figure1_pt2.py` to [../scripts/](../scripts/).

### `superseded_analyses/rebecca_paper_figures/`

A one-off duplicate of `Fig4_Crossvalled_Heatmaps.ipynb`. Use the version in
[../notebooks/figures/](../notebooks/figures/).

### `superseded_analyses/rebecca_ltp_two_photon/`

Two-photon LTP slice imaging and BrightFocus pilot analyses. **A separate
project from this paper** — it shares no data or code with the dCA1 figures and
depends on a different lab share (`/Volumes/DullaLab$/`). Archived rather than
deleted only so the work isn't lost in a repo shuffle; it arguably belongs in
its own repository, and is a reasonable candidate for removal.

### `superseded_analyses/scratch_fig1e_freezing_barplot.py`

A loose plotting snippet (originally the untitled file `scratch fig1e`) for a
grouped freezing bar plot. Superseded by
[behavior_plots.ipynb](../notebooks/supplementary/behavior_plots.ipynb).

---

## Files removed entirely

These were deleted from the working tree in the 2026 reorganisation. All are
recoverable from commit **`f413327`**:

| File | Size | Why removed |
|---|---|---|
| `analysis.ipynb` | 24 MB | Monolithic notebook superseded by the per-figure notebooks; its only surviving outputs are in [../data/processed/legacy_peak_analysis/](../data/processed/legacy_peak_analysis/) |
| `plot_events.ipynb` | 18 MB | Monolithic event-plotting notebook, superseded |
| `movie.mp4`, `test_anim.mp4` | 25 MB | Committed render artefacts |
| `Manifest.toml` (repo root) | 12 KB | Stale duplicate of [../julia/Manifest.toml](../julia/Manifest.toml) for an older Julia (1.11.5 vs 1.12.2), with no matching `Project.toml` |
| `__init__.py` (repo root) | 0 B | The repo root was never an importable package |

To recover one:

```bash
git show f413327:analysis.ipynb > analysis.ipynb
```

Roughly 778 MB of unreferenced intermediate CSVs were also removed from the
working tree. Those were never tracked by git (an old blanket `*.csv` ignore
rule); they were copied to
`dCA1_Clean_Data/archive_orphaned_intermediates/` on the lab share, with
per-file SHA-256 verification recorded in `CHECKSUM_VERIFICATION.csv`
alongside them. See [../data/README.md](../data/README.md#archived-intermediates).

Note that removing the videos from the working tree does **not** shrink
`.git`, which still contains their history. Shrinking it would require a
history rewrite (`git filter-repo`) and coordinated re-clones; that was
deliberately not done.
