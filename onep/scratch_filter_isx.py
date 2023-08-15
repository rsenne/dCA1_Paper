#%%
import pandas as pd 
from cell_registration import CellReg
from onep import InscopixProcessing
cellreg = CellReg('astro5','FOV1',N_sessions=5)
reg_ind = cellreg.get_reg_ind()

data_dir = '/Users/amonast/Desktop/dCA1_astro'
animal = 'astro5'
session= 'fc'
isx = InscopixProcessing(session,animal,data_directory=data_dir)
isx.read_inscopix()


#%% 
def filter_all_isx:
    if session_inds is None:
            n_sessions = 5
        ## for session in range(n_sessions):
# %%
def filter_session(traces,cell_class=='accepted')
    
    

    if cell_class=='accepted':

    elif cell_class=='rejected':
        pass



    #%%

    ### test it out 
    ## plot one cell roi next to its trace before filter
    ## print filtered indices
    ## plot the same cell after filtering 