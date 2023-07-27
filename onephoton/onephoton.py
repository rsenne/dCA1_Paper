#%%
from cell_registration import CellReg
import numpy as np
import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm
import matplotlib.pyplot as plt
import os 

__all__ = ["InscopixProcessing"]

#%%
class InscopixProcessing():
    def __init__(self, filename, animal, data_directory = None):
        self.filename = filename
        self.all_cells = None
        self.rejected = None
        self.accepted = None
        self.animal = animal

        if data_directory is not None:
            self.CellReg_path = os.path.join(data_directory,'CellReg')
    
    def read_inscopix(self):
        df = pd.read_csv(self.filename, header=[0, 1], index_col=0)
        # accepted needs a space because these files were saved poorly
        accepted_cells = df.xs(" accepted", axis=1, level=1)
        rejected_cells = df.xs(" rejected", axis=1, level=1)
        self.accepted = accepted_cells
        self.rejected = rejected_cells
        self.all_cells = df

    def get_registered_cells(self,stable_all=False):
        FOV = 'FOV1'
        reg = CellReg(self.animal,fov=FOV,N_sessions=5,session_inds=None)
        inds_all = reg.load_registration_table()
        inds = inds_all.iloc[:,0:5].copy().astype(int)
        self.reg_inds = inds
        self.stable_inds = self.reg_inds.loc[(inds[0]!=-1) & (inds[1]!=-1) & (inds[2]!=-1) & (inds[3]!=-1) & (inds[4]!=-1)].copy()

        if stable_all:
            return self.stable_inds
        else:
            return self.reg_inds
    
    def classify_cells(self):
        pass

    def event_triggered_average(self):
        pass


# %%
