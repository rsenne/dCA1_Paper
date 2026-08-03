# A hippocampal astrocytic sequence emerges during learning and memory

Analysis code for one-photon calcium imaging of dorsal CA1 astrocytes across
habituation, contextual fear conditioning, and two recall contexts (A and B).

Senne and Suthard et al. 2026, _Nature Neuroscience_ *In press.* 
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
julia/                 Pluto notebook for the sequence detector
docs/                  cell registration pipeline
archive/               superseded analyses, kept for provenance
```
