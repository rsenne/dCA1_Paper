# Archive

Superseded analyses, kept so the provenance of earlier figure versions isn't
lost. **None of this is part of the reproducible pipeline.** Outputs have been
stripped and nothing here has been re-run; most still points at absolute paths
on machines that no longer exist.

## What replaced what

| Archived | Now in |
|---|---|
| `Fig4_Crossvalled_Reactivated`, `Reactivated_Heatmaps` | `notebooks/figures/Fig4_Crossvalled_Heatmaps` |
| `Recall_heatmaps`, `Recall_heatmaps_crossvalled_fig3` | `notebooks/figures/Figure3_Cross_valled` |
| `Supplemental_WaveMAP`, `WaveMAP_output_functions`, `wavemap_posthoc_analysis` | `notebooks/supplementary/Supp_WaveMap` |
| `Sequence_Detector` | `notebooks/supplementary/Seq_Detector` |
| `heatmap_predmu`, `pred_mu_vs_argmax_fc` | `notebooks/figures/Figure2_3_distribution_histograms` |
| `Figure1_plot_footprints` | `scripts/plot_fig1_representative_fov.py` |
| `rebecca_paper_figures/Fig4_Crossvalled_Heatmaps` | duplicate; use `notebooks/figures/` |

`Time_analysis_2024`, `Spearmans_Correlation`, `evan_figure`, `figure2.py`,
`find_events.py`, `traces_umap.py`, `dlc_analysis.py`, `demo_filter_isx.py`,
and the `amy_analyses/` filtering experiments were exploratory and have no
direct successor.

`rebecca_ltp_two_photon/` is two-photon LTP slice work — a different project
that shares no data or code with this paper and depends on another lab share.
It's here only so it wasn't lost in the reshuffle; it probably belongs in its
own repository.

## Promoted out of the archive

Four files in the old `Old_Analyses/` folder were still load-bearing and were
moved into the active tree rather than archived:

- `cell_registration.py` → `onep/` (imported by six other files)
- `cell_registration README.md` → `docs/cell_registration_pipeline.md`
- `Create_WaveMAP_numpy_arrays_CFC_Recall.ipynb` → `notebooks/preprocessing/`
  (builds the array `Supp_WaveMap` reads)
- `eval_cellreg_rebecca.ipynb` → `notebooks/preprocessing/` (registration QC)

Likewise `affine_transform.ipynb` and `save_image_stacks.ipynb` came out of
`amy_analyses/` — they're steps 4–5 of the registration pipeline.

## Deleted files

Removed from the working tree; recover with `git show f413327:<path>`.

| File | Size | Reason |
|---|---|---|
| `analysis.ipynb` | 24 MB | monolith superseded by the per-figure notebooks; its surviving outputs are in `data/processed/legacy_peak_analysis/` |
| `plot_events.ipynb` | 18 MB | monolithic event plotting, superseded |
| `movie.mp4`, `test_anim.mp4` | 25 MB | render artefacts |
| `Manifest.toml` (root) | 12 KB | stale duplicate of `julia/Manifest.toml`, older Julia, no `Project.toml` |
| `__init__.py` (root) | 0 B | repo root was never a package |

About 778 MB of unreferenced intermediate CSVs (`final_df.csv`,
`recall_gen1_df.csv`, `recall_df.csv`, `sequences_astro_*.csv`,
`*_cell_plot_heatmap_mu.csv`, `preprocessed_files/`) were never tracked by git
and now live on the lab share at
`dCA1_Clean_Data/archive_orphaned_intermediates/`, with per-file SHA-256 in
`CHECKSUM_VERIFICATION.csv` next to them.

Deleting the videos didn't shrink `.git`, which still carries their history
along with several 90 MB notebook revisions. Reclaiming that needs
`git filter-repo` and coordinated re-clones, which hasn't been done.
