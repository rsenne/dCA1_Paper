#%%
import numpy as np
import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm
import matplotlib.pyplot as plt
from pathlib import Path
from onep.cell_registration import CellReg
from onep.behavior_analysis import calculate_binned_freezing, create_freeze_vector
__all__ = ["InscopixProcessing"]


class InscopixProcessing():
    def __init__(self, animal, session, directory):
        '''
        directory: data folder (i.e. dCA1_Analysis)
        animal: string, sub-folder for each astro that matches filename (i.e. 'astro3')
        cellreg: file within animal folder (i.e. astro3_cell_reg.csv)
        session: string, sub-folder within animal folder (i.e. 'fc','ext1','gen1')
        traces: file within session folder (i.e. astro3_fc_traces.csv)
        behavior: file within session folder (i.e. astro3_fc_behavior.csv)
        '''
        self.directory = Path(directory)
        self.animal = self.directory/animal
        self.cellreg = self.animal/f"{animal}_cell_reg.csv"
        self.session = self.animal/session
        self.traces = self.session/f"{animal}_{session}_traces.csv"
        self.behavior = self.session/f"{animal}_{session}_behavior.csv"
        self.timestamps = None
        self.freeze_vector = None
        self.binned_freezing = None
        self.all_traces = None
        self.accepted_traces = None
        self.rejected_traces = None

    def read_inscopix(self):
        '''
        Reads Inscopix trace csv file.
        '''
        try:
            df = pd.read_csv(self.traces, header=[0,1], index_col=0)
        except FileNotFoundError:
            raise Exception('traces csv file not found, check folder structure')
        self.all_traces = df

        # accepted vs rejected traces
        # accepted needs a space because these files were saved poorly
        accepted_traces = df.xs(" accepted", axis=1, level=1)
        rejected_traces = df.xs(" rejected", axis=1, level=1)
        self.accepted_traces = accepted_traces
        self.rejected_traces = rejected_traces
        self.timestamps = pd.Series(df.index.to_numpy())

        #accepted vs rejected cell indices
        self.accepted_df= pd.read_csv(self.traces,header=None,index_col=0).iloc[1].map({' accepted':True,' rejected':False}).rename('cell_status').reset_index(drop=True).reset_index()
        self.accepted_inds=self.accepted_df['index'].loc[self.accepted_df['cell_status']==True].values
        self.rejected_inds=self.accepted_df['index'].loc[self.accepted_df['cell_status']==False].values

    def get_traces(self,cell_inds=None):
        '''
        cell_inds: indices of which cell rois to get
        returns: self.traces: N x T array of cell activity
        '''
        try:
            getattr(self,"all_traces")
        except AttributeError:
            self.read_inscopix()

        if cell_inds is not None:
            return self.all_traces.values.T[cell_inds,:]
        else:
            return self.all_traces.values.T

    def load_registration_table(self,filter_accepted=True,session_subset=None):
        '''
        session_subset: (optional) list, session indices (i.e. 0 for fc, 1 for recall, etc.)
        to do filter accepted
        '''
        if session_subset is not None:
            table = CellReg(self.animal, 'FOV1').load_registration_table()
        else:
            table = CellReg(self.animal, 'FOV1', N_sessions=session_subset).load_registration_table()
        return table

    def behavior_analysis(self):
        '''
        Grabs behavioral file for a certain animal + session
        Calculates binned_freezing and creates freeze_vector from the behavioral_analysis.py file
        '''
        self.binned_freezing, anymaze_df = calculate_binned_freezing(self.behavior)
        self.freeze_vector = create_freeze_vector(anymaze_df, self.timestamps)
        return


