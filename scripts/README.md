# Scripts

Run from the repo root with the package installed (`pip install -e .`).

| Script | Purpose | Needs |
|---|---|---|
| `verify_data.py` | verify or regenerate the `data/processed` checksum manifest | — |
| `build_zenodo_archive.py` | package data + code as zips for a Zenodo deposit | imaging, intermediates |
| `Export_Files_Rui.py` | export per-animal accepted traces; produces the intermediates tier | imaging |
| `trace_video_fc_f9.py` | render the FC trace + behaviour movie for F9 | imaging + video, `[video]` |
| `trace_video_cxta_f9.py` | same for recall context A | imaging + video, `[video]` |
| `spatial_timemaps.py` | spatial time-map analysis | imaging |
| `spatial_timemaps_supplemental.py` | supplemental variant | imaging |
| `plot_fig1_representative_fov.py` | representative FOV with footprint overlays | raw, `[cellreg]` |
| `plot_fig1_active_cells.py` | active-cell overlay panel | raw, `[cellreg]` |
| `create_dCA1_M10.py` | build the processed dataset for M10 from raw Inscopix output | raw |