#%%
import numpy as np
import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm
import matplotlib.pyplot as plt
import os 
from .cell_registration import CellReg
__all__ = ["InscopixProcessing"]

#%%
class InscopixProcessing():
    def __init__(self, animal, session, data_directory):
        '''
        animal: string, must match in all filenames
        session: string, must match according to mouse group + filenames (i.e. 'fc','ext1','gen1')
        data_directory: home directory for experiment; contains subfolders for Cell_Traces, CellReg
        '''
        self.CellReg_path = os.path.join(data_directory,'CellReg')
        self.Traces_path = os.path.join(data_directory,'Cell_Traces',animal+'_traces')
        
        # if not os.path.exists(self.CellReg_path):
        #     raise FileNotFoundError("Couldnt find CellReg subfolder, check data directory & subfolders")
        if not os.path.exists(self.Traces_path):
            raise FileNotFoundError("Couldnt find Traces subfolder, check data directory & subfolders")
        
        self.session=session
        self.animal = animal
        self.filename = os.path.join(self.Traces_path,animal+'_'+session+'_traces.csv')
        self.all_traces = None
        self.accepted_traces = None
        self.rejected_traces = None

    def read_inscopix(self):
        '''
        Reads Inscopix trace csv file. 
        '''
        try:
            df = pd.read_csv(self.filename, header=[0,1], index_col=0)
        except FileNotFoundError:
            raise Exception('traces csv file not found, check folder structure')
        self.all_traces = df
        
        # accepted vs rejected traces
        # accepted needs a space because these files were saved poorly
        accepted_traces = df.xs(" accepted", axis=1, level=1) 
        rejected_traces = df.xs(" rejected", axis=1, level=1) 
        self.accepted_traces = accepted_traces
        self.rejected_traces = rejected_traces

        #accepted vs rejected cell indices 
        self.accepted_df= pd.read_csv(self.filename,header=None,index_col=0).iloc[1].map({' accepted':True,' rejected':False}).rename('cell_status').reset_index(drop=True).reset_index()
        self.accepted_inds=self.accepted_df['index'].loc[self.accepted_df['cell_status']==True].values
        self.rejected_inds=self.accepted_df['index'].loc[self.accepted_df['cell_status']==False].values

    def correct_photobleach():
        pass
        
    def get_traces(self,cell_inds=None):
        '''
        cell_inds: indices of which cell rois to get
        returns: self.traces: N x T array of cell activity 

        '''
        if self.all_traces is None:
            self.read_inscopix()

        if cell_inds is not None:
            return self.all_traces.values.T[cell_inds,:]
        else: 
            return self.all_traces.values.T
    
    def load_registration_table(self,filter_accepted=True,session_subset=None):
        '''
        session_subset: (optional) list, session indices (i.e. 0 for fc, 1 for ext1/gen1 for animal with all 5 sessions etc)
        to do filter accepted
        '''
        if session_subset is not None:
            table = CellReg(self.animal,'FOV1',N_sessions=len(session_subset),session_inds=session_subset).load_registration_table()
        else:
            table = CellReg(self.animal,'FOV1').load_registration_table()



    def classify_cells(self):
        pass

    def event_triggered_average(self):
        pass


# %%
