# Sequence detector (Julia)

`activity_detector.jl` is the [Pluto](https://plutojl.org/) notebook
implementing the sequence detector that detects putative astrocyte sequences
("high-activity events"). It produced the event times in
`data/processed/figure3/event_times_cxt{a,b}.csv`.

```bash
julia --project=. -e 'using Pkg; Pkg.instantiate()'
julia --project=. -e 'using Pluto; Pluto.run(notebook="activity_detector.jl")'
```

`Project.toml` / `Manifest.toml` here pin only Pluto (Julia 1.12.2). The
notebook's own dependencies are embedded in the `.jl` file as
`PLUTO_PROJECT_TOML_CONTENTS` / `PLUTO_MANIFEST_TOML_CONTENTS` with exact
versions, and Pluto instantiates them on open — so the notebook is
self-contained: HiddenMarkovModels 0.7.0, Distributions 0.25.120, CSV 0.10.15,
DataFrames 1.7.0, Plots 1.40.14, PlutoUI 0.7.65.
