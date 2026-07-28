# Julia — high-activity sequence detector

[`activity_detector.jl`](activity_detector.jl) is the
[Pluto.jl](https://plutojl.org/) notebook implementing the hidden Markov model
used to detect putative astrocyte sequences ("high-activity events") in the
paper. This is the detector behind the event times in
`data/processed/figure3/event_times_cxt{a,b}.csv`.

## Running it

```bash
julia --project=. -e 'using Pkg; Pkg.instantiate()'
julia --project=. -e 'using Pluto; Pluto.run(notebook="activity_detector.jl")'
```

`Project.toml` / `Manifest.toml` here pin only **Pluto itself** (Julia 1.12.2).
The notebook's own dependencies are embedded in `activity_detector.jl` as
`PLUTO_PROJECT_TOML_CONTENTS` / `PLUTO_MANIFEST_TOML_CONTENTS`, with exact
versions, and Pluto instantiates them automatically on open. That makes the
notebook self-contained and reproducible without any extra setup.

Embedded dependencies: `HiddenMarkovModels` 0.7.0, `Distributions` 0.25.120,
`CSV` 0.10.15, `DataFrames` 1.7.0, `Plots` 1.40.14, `PlutoUI` 0.7.65.

## Model

A two-state HMM over summed ΔF/F is fit per animal per session; the
high-activity state is taken as a putative sequence period. The notebook reads
per-animal `accepted_traces.csv` / `time.csv` exports and writes
`{animal}_events_binary.csv` and `event_times.csv`.

Trace exports are produced by
[../scripts/Export_Files_Rui.py](../scripts/Export_Files_Rui.py) from the tier-2
session collections — see [../data/README.md](../data/README.md).

## Note on paths

This notebook still contains a hardcoded input directory
(`/Users/ryansenne/Desktop/Dill`). Unlike the Python code it has not been
migrated to a configurable data root; set the path in the loading cell before
running. Julia has no equivalent of [`onep.paths`](../onep/paths.py) here.
