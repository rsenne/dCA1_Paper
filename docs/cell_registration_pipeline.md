# Cell Registration Pipeline

Registers astrocyte ROIs across imaging sessions so the same cell can be
followed through habituation, fear conditioning, and both recall contexts.
Required to rebuild the tier-2 session collections; **not** needed to reproduce
the paper figures from `data/processed`.

> **Note on paths.** This document predates the 2026 reorganisation and refers
> to `/BaseDirectory/...`. That is the tier-2 data root — resolve it with
> `onep.paths.data_root()` rather than hardcoding it. See
> [../data/README.md](../data/README.md) for the expected layout, and
> [../onep/cell_registration.py](../onep/cell_registration.py) for the `CellReg`
> class implementing these steps.

Notebooks referenced below now live in
[../notebooks/preprocessing/](../notebooks/preprocessing/).

### Required software

- MATLAB with [CellReg](https://github.com/zivlab/CellReg)
- Inscopix Data Processing Software (IDPS) for ROI extraction and projections
- Python: `pip install -e ".[cellreg]"` from the repo root, which installs
  tifffile, holoviews, matplotlib, scipy, numpy, scikit-image, and pandas

### 1. Folder structure
Create subfolders for each animal's fov

/BaseDirectory/CellReg/{ani}_{FOV}

### 2. Run preprocessing in IDPS software
1) Extract ROIs, save ROI cell tiffs 


2) Export motion corrected mean, min, std dev projections:
- BaseDirectory/Summary_Images/MC/{ani}_{session}_MeanProj_MC.tiff
- BaseDirectory/Summary_Images/MC/{ani}_{session}_MinProj_MC.tiff
- BaseDirectory/Summary_Images/MC/{ani}_{session}_STDProj.tiff
3) Export motion corrected movie as tif: BaseDirectory/Summary_Images/MC/{ani}_{session}_MC_Movie.tiff


4) Export Max DF/F Projection as tif: BaseDirectory/Summary_Images/DFF/{ani}_{session}_maxproj.tiff

### 3. Create correlation images - optional - maybe remove from pipeline. 
1) generate correlation images and save them. *Requires Caiman* 

### 4. Convert Inscopix footprints 
using CellReg's helper file (.../CellReg/Helper/format_conversion_inscopix.m)
 - run for each sessions output folder containing all cell tiffs (Step 1 above)
 - save output for each session as '/BaseDirectory/CellReg/{ani}_{FOV}/converted_maps/{ani}_{session}_G&B_converted.mat

### 5. Manual alignment of FOVS
- [affine_transform.ipynb](../notebooks/preprocessing/affine_transform.ipynb)
    save to savepath: 
    '/BaseDirectory/CellReg/{ani}_{FOV}/shifted_maps/
- TO DO: align sessions pre registration

### 6. Run CellReg
1) Select converted footprint mat files from /BaseDirectory/CellReg/ani_FOV/converted_maps
2) Run Cell Reg, set output directory as /BaseDirectory/CellReg/ani_FOV
3) TODO: redo cell reg after affine transform alignment 

### 7. Run Manual Quality Control
1) [eval_cellreg_rebecca.ipynb](../notebooks/preprocessing/eval_cellreg_rebecca.ipynb)
2) save results as animal_cell_reg.csv 



### Example

```python
from onep import paths
from onep.cell_registration import CellReg
from onep.onephoton import InscopixProcessing

data_dir = paths.data_root()          # resolved per machine, never hardcoded
animal = "astroF9"
session = "fc"

isx = InscopixProcessing(session, animal, data_directory=data_dir)
isx.read_inscopix()

reg = CellReg(animal, fov="FOV1", N_sessions=2, session_inds=[0, 1])
reg_ind = reg.load_registration_table()
```

An example of the resulting registration table is committed at
[`data/processed/cell_registration/astro3_cell_reg.csv`](../data/processed/cell_registration/astro3_cell_reg.csv)
as a format reference.