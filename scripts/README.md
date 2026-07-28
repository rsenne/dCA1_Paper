# Scripts

Standalone entry points. Run from the repo root with the package installed
(`pip install -e .`).

| Script | Purpose | Needs |
|---|---|---|
| [verify_data.py](verify_data.py) | Verify or regenerate the `data/processed` checksum manifest | — |
| [Export_Files_Rui.py](Export_Files_Rui.py) | Export per-animal accepted traces from a session collection to CSV, as input to the generative peak-time model | tier 2 |
| [trace_video_fc_f9.py](trace_video_fc_f9.py) | Render the FC trace + behaviour movie for animal F9 (extended data video) | tier 2 + behaviour video, `[video]` |
| [trace_video_cxta_f9.py](trace_video_cxta_f9.py) | Same for the context A recall session | tier 2 + behaviour video, `[video]` |
| [spatial_timemaps.py](spatial_timemaps.py) | Spatial time-map analysis of astrocyte events | tier 2 |
| [spatial_timemaps_supplemental.py](spatial_timemaps_supplemental.py) | Supplemental variant of the above | tier 2 |
| [plot_fig1_representative_fov.py](plot_fig1_representative_fov.py) | Representative FOV with cell footprint overlays | tier 3, `[cellreg]` |
| [plot_fig1_active_cells.py](plot_fig1_active_cells.py) | Active-cell overlay panel | tier 3, `[cellreg]` |
| [create_dCA1_M10.py](create_dCA1_M10.py) | Build the processed dataset for animal M10 from raw Inscopix output | tier 3 |

"tier 2 / tier 3" refer to the data tiers in [../data/README.md](../data/README.md).
Extras in brackets are optional dependency groups: `pip install -e ".[video]"`.

## Usage

```bash
python scripts/verify_data.py                    # verify committed data
python scripts/verify_data.py --check-upstream    # also check tier 2 reachability
python scripts/verify_data.py --write            # regenerate the manifest
```

## Caveats

The video-rendering and figure-plotting scripts were written as one-off
analyses against specific animals and sessions, and several still contain
hardcoded animal IDs (`F9`) and expect behaviour `.avi` files that live only on
the lab share. They are kept because they generated published extended-data
videos and figure panels, but they are **not** part of the reproducible
`data/processed` path — treat them as documentation of how those assets were
made. `verify_data.py` is the only script here that runs against a bare clone.
