#%%
import pandas as pd
from onep.cell_registration import CellReg
from onep.onephoton import InscopixProcessing
cellreg = CellReg('astro5','FOV1',N_sessions=5)
reg_ind = cellreg.get_reg_ind()

data_dir = '/Users/amonast/Desktop/dCA1_astro'
animal = 'astro5'
### Examples###
## grab cells from one day, accepted indices only
session= 'fc'
isx = InscopixProcessing(animal,session,data_directory=data_dir)
isx.read_inscopix()
traces=isx.get_traces(cell_inds=isx.accepted_inds)

## grab registered traces from 2 sessions (i.e. FC/Recall)
reg1 = CellReg(animal,fov='FOV1',N_sessions=5,session_inds=None)
reg_ind1 = reg1.load_registration_table()
#%%
reg = CellReg(animal,fov='FOV1',N_sessions=2,session_inds=[2,3])
reg_ind = reg.load_registration_table()

# %%
