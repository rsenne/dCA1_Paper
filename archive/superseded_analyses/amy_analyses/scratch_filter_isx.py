#%%
import pandas as pd 
from onep.cell_registration import CellReg
from onep import InscopixProcessing
cellreg = CellReg('astro5','FOV1',N_sessions=5)
reg_ind = cellreg.get_reg_ind()

data_dir = '/Users/amonast/Desktop/dCA1_astro'
animal = 'astro5'
session= 'fc'
isx = InscopixProcessing(session,animal,data_directory=data_dir)
isx.read_inscopix()

reg = CellReg(animal,fov='FOV1',N_sessions=2,session_inds=[0,1])
reg_ind = reg.load_registration_table()

# %%
