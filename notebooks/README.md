# Notebooks

| Folder | Contents |
|---|---|
| `figures/` | main paper figures |
| `supplementary/` | supplemental figures and statistics |
| `preprocessing/` | rebuilding processed data from raw imaging |

The figure-to-notebook map, including which data tier each one needs and
whether it currently runs, is in the [root README](../README.md#figures).

## Running them

```bash
pip install -e .        # from the repo root
python -m onep.paths    # check what resolves on this machine
```

Paths go through `onep.paths`:

| Call | Returns |
|---|---|
| `paths.processed(*parts)` | file in `data/processed`; on a miss, lists what's actually there |
| `paths.collection(session)` | `hab` / `fc` / `cxta` / `cxtb` pickle (imaging tier) |
| `paths.traces(animal, session)` | per-animal trace CSV (imaging tier) |
| `paths.figure_path(*parts)` | output path under `results/figures`, parents created |
| `paths.data_root(required=False)` | imaging tier root, or `None` |

For a notebook that needs the imaging tier, fail early and clearly:

```python
if paths.data_root(required=False) is None:
    raise RuntimeError("Needs the imaging dataset; see data/README.md")
```

## Outstanding work

Eight supplementary notebooks and all four preprocessing notebooks still
contain absolute paths from the machines they were written on
(`/Users/suthardr/Desktop/...`, `C:\Users\ryansenne\Desktop\Dill\...`). They
have not been migrated to `onep.paths` and have not been re-run. To migrate one:

1. Replace each path literal with the matching `paths.*` call.
2. Run it top to bottom in a fresh kernel.
3. Update the "Runs" column in the root README.

Watch for two problems that showed up in the notebooks already migrated:

- **Kernel-state leakage.** Several notebooks referenced names that were never
  imported anywhere in the file (`ttest_rel`, `_HAS_PG`) and only worked because
  the author's kernel had them from an earlier session. A fresh-kernel run is
  the only way to catch this.
- **Split string literals.** `("/long/path/" "rest.csv")` uses implicit
  concatenation; replacing only the first half silently breaks the expression.
- **`paths.*` returns `Path`, not `str`.** Code that did `save_path.split('.')`
  to get a file extension breaks. Use `str(save_path)` or `save_path.suffix`.
  Passing a `Path` to `savefig`, `read_csv`, or `open` is fine.

And one rule: **never write into `data/processed`.** It is the committed,
checksummed input tier. Derived tables belong in `results/` via
`paths.figure_path(...)`. If `verify_data.py` reports `CHANGED`, a notebook has
overwritten committed data — restore it with `git checkout -- data/processed`.

## Outputs

Executed outputs are committed for `figures/` and `supplementary/` as a record
of expected output, which makes diffs noisy. For clean diffs locally:

```bash
pip install nbstripout && nbstripout --install
```

Notebooks in `../archive/` already have outputs stripped.
