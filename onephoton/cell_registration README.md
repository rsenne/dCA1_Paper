# Cell Registration Pipeline

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

### 3. Convert Inscopix footprints 
using CellReg's helper file (.../CellReg/Helper/format_conversion_inscopix.m)
 - run for each sessions output folder containing all cell tiffs (Step 1 above)
 - save output for each session as '/BaseDirectory/CellReg/{ani}_{FOV}/converted_maps/{ani}_{session}_G&B_converted.mat

### 4. Manual alignment of FOVS
- TO DO: affine_transform.ipynb
- TO DO: align sessions pre registration

### 5. Run CellReg
1) Select converted footprint mat files from /BaseDirectory/CellReg/ani_FOV/converted_maps
2) Run Cell Reg, set output directory as /BaseDirectory/CellReg/ani_FOV
3) TODO: redo cell reg after affine transform alignment 

### 6. Run Manual Quality Control
1) TODO: clean up eval_cellreg.ipynb
2) TODO: Test CellReg class and debug, download example images 