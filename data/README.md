# Data

| Tier | Contents | Size | In git? |
|---|---|---|---|
| Processed | per-figure summary tables and arrays | 26 MB | yes, `processed/` |
| Imaging | session collections + Inscopix cell traces | ~820 MB | no — Zenodo / lab share |
| Intermediates | trace exports, event times, freeze vectors, DLC pose | ~510 MB | no — Zenodo / lab share |
| Raw | `.isxd` movies, CellReg output, behaviour video | tens of GB | no — lab share only |

Most published figures are plotted from the processed tier alone. The imaging
tier is needed by the cross-validated sequence figures; the intermediates tier
by six supplementary analyses.

## Verifying

`MANIFEST.sha256` lists the SHA-256 and size of all 42 processed files.

```bash
python ../scripts/verify_data.py                    # verify
python ../scripts/verify_data.py --write            # regenerate after intentional edits
python ../scripts/verify_data.py --check-upstream    # look for the imaging tier
```

These files are marked `-text` in `.gitattributes`, so they're stored
byte-for-byte and checksums match on Windows and macOS.

## Provenance

Everything in `processed/` was copied from the lab share at
`dCA1_Clean_Data/Revision1/` (round-1 revision outputs) and
`dCA1_Clean_Data/Anymaze/`. Original locations are listed so any file can be
traced back.

### `figure1/` — registration counts

| File | Origin |
|---|---|
| `Normalized_UniqueCells_FC_Pair.csv` | `Revision1/Figure1_background/` |
| `registration_counts_wide.csv` | `Revision1/Figure1_background/data.csv` |
| `registration_counts_long.csv` | `Revision1/Figure1_background/long_data.csv` |

Renamed from `data.csv` / `long_data.csv`. Columns: per-animal cell counts
(`Across_Sessions`, `Unique_FC`, `Unique_Cond`, `Unique_Total`) with `Animal`,
`Sex`, `Order`, `Session_Pair`, plus derived percentages.

Note: `Fig1_total_cells_and_reactivated.ipynb` originally read a file called
`long_form_registration_data.csv` from a directory that no longer exists on the
share. `registration_counts_wide.csv` is a superset of it (same rows, plus
`pct_overlap`), so the notebook now reads that instead.

### `figure2/`, `figure3/`, `figure4/`

Cross-validated sequence statistics: Spearman ρ between event-triggered peak
times in one half of trials vs the other, per animal, with shuffle nulls.

| File | Origin |
|---|---|
| `figure2/crossval_summary_results.csv` | `Revision1/Figure2_FC/Crossvalled_FC/` |
| `figure3/crossval_summary_results_cxt{a,b}.csv` | `Revision1/Figure3_Recall/crossvalled_Fig3/` |
| `figure3/Num_Detected_Events.csv` | `Revision1/Figure3_Recall/num_events_Fig3/` |
| `figure3/event_times_cxt{a,b}.csv` | `Revision1/Figure3_Recall/num_events_Fig3/` |
| `figure4/*` | `Revision1/Figure4_Reactivated/no_F8/` |

Figure 4 comes from the `no_F8` variant — the version used in the paper, with
animal F8 excluded. A `dontuse/` variant also exists on the share and was
deliberately not copied.

### `modeling/`

Output of the Gaussian-noise generative model of astrocyte event timing, from
`Revision1/rui_modeling_plots_csv/`. `pred_mu` is the model-predicted peak time
per cell.

`astrocyte_shot_Gaussian_noise3_all.csv` (fear conditioning),
`astrocyte_NEWcxtA_...` (recall A), `astrocyte_NEWcxtB_...` (recall B),
`astrocyte_NEWhab_Gaussian_noise3_all.csv` (habituation).

The habituation table was not on the share — it existed only in a local working
folder and was copied in here, with the `(1)` download suffix dropped from the
filename. It has eight `mu_*` columns to the others' four.

### `supplementary/`

| File | Origin |
|---|---|
| `wavemap/revision_umap_cfc_allmice_30_01.csv` | UMAP embedding + Louvain labels (n_neighbors=30, min_dist=0.1) |
| `wavemap/..._with_animal.csv` | as above with animal IDs |
| `wavemap/shock_epoch_cells_x_time_z.npy` | z-scored cells × time matrix, shock epoch (UMAP input) |
| `wavemap/shock_epoch_time.npy` | time axis |
| `wavemap/shock_epoch_animal_ids.{npy,csv}` | animal per row |
| `first_v_second/crossval_summary_results.csv` | FC cross-validation, first vs second half |
| `ihc/IHC_Counts.csv` | GFAP colocalisation counts for viral specificity |

WaveMAP files come from the `withoutF8` variant, which is the one reported.

### `behavior/`

Per-session AnyMaze freezing summaries from `dCA1_Clean_Data/Anymaze/`:
`hab_freezing.csv`, `fc_freezing.csv`, `cxta_freezing.csv`, `cxtb_freezing.csv`.

### `cell_registration/`

`astro3_cell_reg.csv` — an example CellReg output (cell index mapping across
sessions), kept as a format reference for
[../docs/cell_registration_pipeline.md](../docs/cell_registration_pipeline.md).

### `legacy_peak_analysis/`

Small result tables from an earlier peak-width and activity–freezing analysis
predating the round-1 revision. Kept because they're the only surviving
artefacts of it; the notebook that produced them (`analysis.ipynb`) was removed
and is recoverable from git (see [../archive/README.md](../archive/README.md)).
No current figure uses them.

## The imaging and intermediates tiers

Layout `onep.paths` expects:

```
dCA1_Clean_Data/
├── Dill/collection_{hab,fc,cxta,cxtb}_allmice.pkl    50 / 189 / 119 / 85 MB
├── Cell_Traces/{animal}_traces/{animal}_{session}_traces.csv     ~375 MB
├── Anymaze/{session}_freezing.csv
├── CellReg/{animal}_FOV1/                            (raw tier)
└── Derived_Exports/                                  intermediates tier
    ├── {session}_traces_csv/   accepted traces, event_times, freeze vectors
    ├── dlc/                    DeepLabCut pose output
    └── Time.csv
```

Sessions: `hab`, `fc`, `cxta`, `cxtb`. Animals: `astroF3`, `astroM3`, … (F/M =
sex).

```python
from onep import paths

paths.collection("fc")                                  # Dill/collection_fc_allmice.pkl
paths.traces("astroF9", "cxta")                         # Cell_Traces/...
paths.intermediate("fc_traces_csv", "event_times.csv")  # Derived_Exports/...
paths.data_root(required=False)                         # None if unavailable
paths.intermediates(required=False)                     # None if unavailable
```

Set `DCA1_DATA_ROOT` for the imaging tier and, if it lives outside
`<data root>/Derived_Exports`, `DCA1_INTERMEDIATES` for the intermediates. Both
also take a key in `config.ini`. Ramirez lab mounts are detected automatically,
including the `\\nas1.bu.edu` UNC path.

`Derived_Exports/` is regenerable:
`python scripts/Export_Files_Rui.py --session fc` (and `cxta`/`cxtb`/`hab`) for
the trace exports, then the Pluto notebook in [../julia/](../julia/) for the
event times.

### Publishing

`scripts/build_zenodo_archive.py` packages both tiers plus a snapshot of the
repository as five zips, with a checksum manifest, a deposit README, and
`zenodo_metadata.json`:

| Archive | Contents |
|---|---|
| `dca1_code_<sha>.zip` | the repository at HEAD, including `data/processed` |
| `dca1_collections.zip` | the four session collections |
| `dca1_cell_traces.zip` | per-animal Inscopix trace exports |
| `dca1_derived_intermediates.zip` | the intermediates tier |
| `dca1_behavior.zip` | AnyMaze freezing scores |

```bash
python scripts/build_zenodo_archive.py --dry-run
python scripts/build_zenodo_archive.py --out /path/to/staging
python scripts/build_zenodo_archive.py --out /path --only code   # code alone
```

It uploads nothing. Record the DOI here and in the root README once published.

### Archived intermediates

About 778 MB of unreferenced intermediate tables (`final_df.csv`,
`recall_gen1_df.csv`, `recall_df.csv`, `sequences_astro_*.csv`,
`*_cell_plot_heatmap_mu.csv`, `preprocessed_files/`) were moved to
`dCA1_Clean_Data/archive_orphaned_intermediates/` with per-file SHA-256
verification in `CHECKSUM_VERIFICATION.csv`. No code referenced them.
