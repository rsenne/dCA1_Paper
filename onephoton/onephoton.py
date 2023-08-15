#%%
import numpy as np
import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm
import matplotlib.pyplot as plt
import os 
from cell_registration import *
__all__ = ["InscopixProcessing"]

#%%
class InscopixProcessing():
    def __init__(self, session, animal, data_directory):
        '''
        animal: string, must match in all filenames
        session: string, must match in all filenames 
        data_directory: home directory for experiment; contains subfolders for Cell_Traces, CellReg
        '''
        try:
            self.CellReg_path = os.path.join(data_directory,'CellReg')
            self.Traces_path = os.path.join(data_directory,'Cell_Traces',animal+'_traces')
        except OSError:
            print("Couldnt find CellReg + Traces subfolders, check data directory & subfolders")
        
        self.animal = animal
        self.filename = os.path.join(self.Traces_path,animal+'_'+session+'_traces.csv')
        self.all_cells = None
        
    def read_inscopix(self):
        df = pd.read_csv(self.filename, header=[0,1], index_col=0)
        # accepted needs a space because these files were saved poorly
        accepted_cells = df.xs(" accepted", axis=1, level=1) 
        rejected_cells = df.xs(" rejected", axis=1, level=1) 
        self.accepted_cells = accepted_cells
        self.rejected_cells = rejected_cells

        accepted_df = pd.read_csv(self.filename,header=None,index_col=0).iloc[1].map({' accepted':True,' rejected':False}).rename('cell_status').reset_index(drop=True).reset_index()
        self.accepted=accepted_df['index'].loc[accepted_df['cell_status']==True].values
        self.rejected=accepted_df['index'].loc[accepted_df['cell_status']==False].values
        self.all_cells = df

    def get_traces(self,type='dff',cell_inds=None):
        self.read_inscopix()
        traces = self.all_cells.values.T
        if cell_inds is not None:
            return self.all_cells
        else: 
            return self.all_cells
    
    def get_registered_cells(self,filter_accepted=True,stable_all=False,session_subset=None):
        '''
        stable all: bool set True for cells across all 5 sessions
        session_subset: list, pass indices of session for registered cells; gives overlapping cells only.
                        default None returns full look up table of registered indices
        
        returns: 
            self.reg_inds: look up table of registered indices; filtered if specified by kwargs above
        '''
        FOV = 'FOV1'
        reg = CellReg(self.animal,fov=FOV,N_sessions=5,session_inds=None)
        inds_all = reg.load_registration_table()
        inds = inds_all.iloc[:,0:5].copy().astype(int)

        ## filter out the accepted/rejected
        
        self.stable_inds = inds.loc[(inds[0]!=-1) & (inds[1]!=-1) & (inds[2]!=-1) & (inds[3]!=-1) & (inds[4]!=-1)].copy()

        if stable_all:
            return self.stable_inds
        elif session_subset is not None:
            print('Only getting overlap cells for sessions: ')
            sessions = [reg.sessions[i] for i in session_subset]
            print(sessions)
            n_sessions = len(session_subset)
            reg_all = inds.iloc[:,0:n_sessions+1].copy()
            
            try:
                if len(session_subset) == 2:
                    reg_inds= reg_all.loc[(reg_all[session_subset[0]]!=-1) & (reg_all[session_subset[1]]!=-1)].copy()
                elif len(session_subset) == 3:
                    reg_inds = reg_all.loc[(reg_all[session_subset[0]]!=-1) & (reg_all[session_subset[1]]!=-1) & (reg_all[session_subset[2]]!=-1)].copy().iloc[:,0:1]
                elif len(session_subset) == 4:
                    reg_inds= reg_all.loc[(reg_all[session_subset[0]]!=-1) & (reg_all[session_subset[1]]!=-1) & (reg_all[session_subset[2]]!=-1)&(reg_all[session_subset[3]]!=-1)].copy()
            except IndexError:
                print('Session subset must be between 2 and 4')
            self.reg_inds = reg_inds
            return self.reg_inds
         
        else:
            self.reg_inds = inds
            return self.reg_inds
    
    def classify_cells(self):
        pass

    def event_triggered_average(self):
        pass


# %%
