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

Tiers are defined in [../data/README.md](../data/README.md). Bracketed names are
optional dependency groups (`pip install -e ".[video]"`).

## Common use

```bash
python scripts/verify_data.py                        # check the committed data
python scripts/verify_data.py --check-upstream        # is the imaging tier reachable?

python scripts/build_zenodo_archive.py --dry-run      # what would be deposited
python scripts/build_zenodo_archive.py --out /path/to/staging
python scripts/build_zenodo_archive.py --out /path --only code   # code archive alone

python scripts/Export_Files_Rui.py --session fc       # regenerate trace exports
```

`build_zenodo_archive.py` builds five zips — the four session collections, the
per-animal cell traces, the derived intermediates, the behaviour scores, and a
`git ls-files` snapshot of the repository at HEAD — plus `MANIFEST.sha256`, a
deposit `README.md`, and `zenodo_metadata.json`. It excludes `bad_donotuse/`,
`Summary_Images/` and similar scratch directories, and reports what it skipped.

It uploads nothing. Review the staging directory before depositing; a published
Zenodo DOI cannot be withdrawn.

## Caveats

The video and FOV-plotting scripts were written as one-offs against particular
animals and sessions. Several still hardcode animal IDs (`F9`) and paths to
behaviour `.avi` files that exist only on the lab share. They're kept because
they produced published extended-data videos and figure panels, but they are
not part of the reproducible path and have not been migrated to `onep.paths`.
`verify_data.py` is the only script here that runs against a bare clone.
