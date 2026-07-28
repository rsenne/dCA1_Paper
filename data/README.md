# Data

## Tiers

| Tier | Contents | Size | Tracked in git? |
|---|---|---|---|
| 1. **Processed** | Per-figure summary tables and arrays | 26 MB | **Yes** — `processed/` |
| 2. **Upstream** | Session collections + raw Inscopix traces | ~940 MB | No — lab share |
| 3. **Raw** | Inscopix `.isxd` movies, CellReg outputs, behaviour video | Many GB | No — lab share |

Every figure in the paper is generated from **tier 1 alone**. Tiers 2–3 are only
needed to rebuild tier 1 from scratch.

## Verifying integrity

`MANIFEST.sha256` records the SHA-256 and byte size of all 41 tier-1 files.

```bash
python ../scripts/verify_data.py                    # verify
python ../scripts/verify_data.py --write            # regenerate after intentional changes
python ../scripts/verify_data.py --check-upstream    # report on tier 2
```

Tier-1 files are marked `-text` in `.gitattributes`, so they are stored
byte-for-byte and checksums match on Windows and macOS alike.

---

## `processed/` contents and provenance

All tier-1 files were copied from the lab share at
`dCA1_Clean_Data/Revision1/` (the round-1 revision analysis outputs) and
`dCA1_Clean_Data/Anymaze/`. Original locations are given below so any file can
be traced back.

### `figure1/` — cell registration counts

| File | Origin | Description |
|---|---|---|
| `Normalized_UniqueCells_FC_Pair.csv` | `Revision1/Figure1_background/` | Unique cells per session pair, normalised to FC |
| `registration_counts_wide.csv` | `Revision1/Figure1_background/data.csv` | Per-animal registered/reactivated counts, wide form |
| `registration_counts_long.csv` | `Revision1/Figure1_background/long_data.csv` | Same, long form for plotting |

Renamed from the uninformative `data.csv` / `long_data.csv`.

### `figure2/` — fear conditioning sequences

| File | Origin | Description |
|---|---|---|
| `crossval_summary_results.csv` | `Revision1/Figure2_FC/Crossvalled_FC/` | Cross-validated sequence ρ per animal, with shuffle null |

### `figure3/` — recall

| File | Origin | Description |
|---|---|---|
| `crossval_summary_results_cxta.csv` | `Revision1/Figure3_Recall/crossvalled_Fig3/` | Cross-validated ρ, context A |
| `crossval_summary_results_cxtb.csv` | `Revision1/Figure3_Recall/crossvalled_Fig3/` | Cross-validated ρ, context B |
| `Num_Detected_Events.csv` | `Revision1/Figure3_Recall/num_events_Fig3/` | Detected event counts per animal/context |
| `event_times_cxta.csv` | `Revision1/Figure3_Recall/num_events_Fig3/` | Detected event onset times, context A |
| `event_times_cxtb.csv` | `Revision1/Figure3_Recall/num_events_Fig3/` | Detected event onset times, context B |

### `figure4/` — reactivated cells

Taken from the `no_F8/` variant, which is the version used in the paper
(animal F8 excluded). A `dontuse/` variant also exists on the share and was
deliberately **not** copied.

| File | Origin | Description |
|---|---|---|
| `FC_crossval_reactivation_summary_CxtA_CxtB.csv` | `Revision1/Figure4_Reactivated/no_F8/` | Reactivated-cell sequence reinstatement, FC → CxtA/CxtB |
| `crossval_summary_results_cxta.csv` | `Revision1/Figure4_Reactivated/no_F8/` | Cross-validated ρ, reactivated cells, context A |
| `crossval_summary_results_cxtb.csv` | `Revision1/Figure4_Reactivated/no_F8/` | Cross-validated ρ, reactivated cells, context B |
| `Fig4_FCvsRecall_shuffle_summary.csv` | `.../no_F8/shuffle_FC_vs_recall/` | FC vs recall shuffle-null comparison |

### `modeling/` — generative peak-time model

Outputs of the Gaussian-noise generative model of astrocyte event timing,
from `Revision1/rui_modeling_plots_csv/`. Column `pred_mu` is the
model-predicted peak time per cell.

| File | Session |
|---|---|
| `astrocyte_shot_Gaussian_noise3_all.csv` | Fear conditioning (shock) |
| `astrocyte_NEWcxtA_Gaussian_noise3_all.csv` | Recall context A |
| `astrocyte_NEWcxtB_Gaussian_noise3_all.csv` | Recall context B |

### `supplementary/`

| File | Origin | Description |
|---|---|---|
| `wavemap/revision_umap_cfc_allmice_30_01.csv` | `Revision1/Supp_Figures/WaveMap_Supplemental/withoutF8/` | UMAP embedding + Louvain cluster labels (n_neighbors=30, min_dist=0.1) |
| `wavemap/revision_umap_cfc_allmice_30_01_with_animal.csv` | same | As above, with animal IDs joined |
| `wavemap/shock_epoch_cells_x_time_z.npy` | same | Z-scored cells × time matrix for the shock epoch (WaveMAP input) |
| `wavemap/shock_epoch_time.npy` | same | Time axis for the above |
| `wavemap/shock_epoch_animal_ids.{npy,csv}` | same | Animal ID per row of the matrix |
| `first_v_second/crossval_summary_results.csv` | `Revision1/Supp_Figures/1stV2ndFC_Supplemental/first_v_second/` | FC cross-validation, first vs second half |
| `ihc/IHC_Counts.csv` | `Revision1/Supp_Figures/IHC Supplemental/` | GFAP/marker colocalisation counts for viral specificity |

The `withoutF8` WaveMAP variant is the one reported.

### `behavior/` — AnyMaze freezing

Per-session freezing summaries from `dCA1_Clean_Data/Anymaze/`, one row per
animal per time bin.

`hab_freezing.csv`, `fc_freezing.csv`, `cxta_freezing.csv`, `cxtb_freezing.csv`

### `cell_registration/`

`astro3_cell_reg.csv` — an example CellReg output table (cell index mapping
across sessions) kept as a format reference for
[docs/cell_registration_pipeline.md](../docs/cell_registration_pipeline.md).

### `legacy_peak_analysis/`

Small result tables from an **earlier** peak-width/activity-freezing analysis
that predates the round-1 revision. Retained because they are the only
surviving artefacts of that analysis; the notebook that produced them
(`analysis.ipynb`) was removed during the 2026 reorganisation and is
recoverable from git history (see [../archive/README.md](../archive/README.md)).
**Not** used by any current figure.

---

## Tier 2: the upstream dataset

Layout expected by [`onep.paths`](../onep/paths.py):

```
dCA1_Clean_Data/
├── Dill/
│   ├── collection_hab_allmice.pkl      #  52 MB
│   ├── collection_fc_allmice.pkl       # 198 MB
│   ├── collection_cxta_allmice.pkl     # 124 MB
│   └── collection_cxtb_allmice.pkl     #  89 MB
├── Cell_Traces/
│   └── {animal}_traces/{animal}_{session}_traces.csv     # ~474 MB total
├── CellReg/
│   └── {animal}_FOV1/                  # registration outputs
└── Anymaze/                            # behaviour (tier-1 summaries copied from here)
```

Sessions are `hab`, `fc`, `cxta`, `cxtb`. Animals are named `astroF3`,
`astroM3`, … (`F`/`M` denoting sex).

Access it via the API rather than literal paths:

```python
from onep import paths

paths.collection("fc")               # -> .../Dill/collection_fc_allmice.pkl
paths.traces("astroF9", "cxta")      # -> .../Cell_Traces/astroF9_traces/astroF9_cxta_traces.csv
paths.data_root(required=False)      # -> None if unavailable, for graceful fallback
```

Configure the location with `DCA1_DATA_ROOT` or `config.ini` (see
`config.example.ini`). Known lab mounts are auto-detected.

### Archived intermediates

~778 MB of unreferenced intermediate tables (`final_df.csv`,
`recall_gen1_df.csv`, `recall_df.csv`, `sequences_astro_*.csv`,
`*_cell_plot_heatmap_mu.csv`, `preprocessed_files/`) were moved off this repo
during the 2026 reorganisation to
`dCA1_Clean_Data/archive_orphaned_intermediates/`, with
`CHECKSUM_VERIFICATION.csv` recording the SHA-256 of each file as verified at
copy time. No code in this repository referenced them.

### Publishing for the paper

Tier 2 should be deposited in a repository that issues a DOI (Zenodo, DANDI,
or Figshare) at acceptance, and the DOI recorded here and in the root README.
Tier 1 is already citable via this repository's git history.
