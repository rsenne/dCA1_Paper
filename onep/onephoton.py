# %%
import numpy as np
#import jax
import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm
import matplotlib.pyplot as plt
import pykalman
from scipy.sparse.linalg import spsolve
from scipy import sparse
from joblib import Parallel, delayed
from dlc_analysis import dlcResults
import os
from cell_registration import CellReg
from tqdm import tqdm
__all__ = ["InscopixProcessing", "dCA1Group"]


# %%
class InscopixProcessing():
    def __init__(self, animal, session, data_directory):
        '''
        animal: string, must match in all filenames
        session: string, must match according to mouse group + filenames (i.e. 'fc','ext1','gen1')
        data_directory: home directory for experiment; contains subfolders for Cell_Traces, CellReg
        '''
        self.base_dir = data_directory
        self.rejected_inds = None
        self.accepted_inds = None
        self.accepted_df = None
        self.CellReg_path = os.path.join(data_directory, 'CellReg')
        self.Traces_path = os.path.join(data_directory, 'Cell_Traces', animal + '_traces')

        if not os.path.exists(self.CellReg_path):
            raise FileNotFoundError("Couldnt find CellReg subfolder, check data directory & subfolders")
        if not os.path.exists(self.Traces_path):
            raise FileNotFoundError("Couldn't find Traces subfolder, check data directory & subfolders")

        self.session = session
        self.animal = animal
        self.filename = os.path.join(self.Traces_path, animal + '_' + session + '_traces.csv')
        self.all_traces = None
        self.accepted_traces = None
        self.rejected_traces = None
        self.DLC = None
        self.anymaze = None

    def read_inscopix(self):
        """
        Reads Inscopix trace csv file.
        """
        try:
            df = pd.read_csv(self.filename, header=[0, 1], index_col=0)
        except FileNotFoundError:
            raise Exception('traces csv file not found, check folder structure')
        self.all_traces = df

        # accepted vs rejected traces
        # accepted needs a space because these files were saved poorly
        accepted_traces = df.xs(" accepted", axis=1, level=1)
        rejected_traces = df.xs(" rejected", axis=1, level=1)
        self.accepted_traces = accepted_traces
        self.rejected_traces = rejected_traces

        # accepted vs rejected cell indices
        self.accepted_df = pd.read_csv(self.filename, header=None, index_col=0).iloc[1].map(
            {' accepted': True, ' rejected': False}).rename('cell_status').reset_index(drop=True).reset_index()
        self.accepted_inds = self.accepted_df['index'].loc[self.accepted_df['cell_status'] == True].values
        self.rejected_inds = self.accepted_df['index'].loc[self.accepted_df['cell_status'] == False].values

    @staticmethod
    def _als_detrend(y, lam=10e7, p=0.05, niter=100):  # asymmetric least squares smoothing method
        """_summary_

        Args:
            y (_type_): _description_
            lam (_type_, optional): _description_. Defaults to 10e7.
            p (float, optional): _description_. Defaults to 0.05.
            niter (int, optional): _description_. Defaults to 100.

        Returns:
            _type_: _description_
        """
        L = len(y)
        D = sparse.diags([1, -2, 1], [0, -1, -2], shape=(L, L - 2))
        D = lam * D.dot(D.transpose())  # Precompute this term since it does not depend on `w`
        w = np.ones(L)
        W = sparse.spdiags(w, 0, L, L)
        z = np.zeros(len(y))
        for i in range(niter):
            W.setdiag(w)  # Do not create a new matrix, just update diagonal values
            Z = W + D
            z = spsolve(Z, w * y)
            w = p * (y > z) + (1 - p) * (y < z)
        return y - z

    def apply_detrend(self):
        # Using joblib for parallel column processing
        results = Parallel(n_jobs=-1)(delayed(self._als_detrend)(self.accepted_traces[col].values) for col in self.accepted_traces.columns)

        # Replacing old columns with detrended results
        for col, new_data in zip(self.accepted_traces.columns, results):
            self.accepted_traces.loc[:, col] = new_data
    @staticmethod
    
    def kalman_smoother(signal):
        """_summary_

                Args:
                    signal (_type_): _description_

                Returns:
                    _type_: _description_
                """
        ar_model = sm.tsa.ARIMA(signal, order=(3, 0, 0), trend='n').fit()
        A = np.zeros((3, 3))
        A[:, 0] = ar_model.params[:-1]
        A[1, 0] = 1
        A[2, 1] = 1
        H = np.array([1, 0, 0])
        kf = pykalman.KalmanFilter(transition_matrices=A, observation_matrices=H, initial_state_covariance=np.eye(3),
                                   initial_state_mean=(0, 0, 0),
                                   em_vars=['transition_covariance', 'observation_covariance'])
        kf.em(signal, em_vars=['transition_covariance', 'observation_covariance'])
        means, covs = kf.smooth(signal)
        return means[:, 0]

    def apply_smoother(self):
        # Using joblib for parallel column processing
        results = Parallel(n_jobs=-1)(delayed(self.kalman_smoother)(self.accepted_traces[col].values) for col in self.accepted_traces.columns)

        # Replacing old columns with detrended results
        for col, new_data in zip(self.accepted_traces.columns, results):
            self.accepted_traces.loc[:, col] = new_data
        return

    def get_traces(self, cell_inds=None):
        """
        cell_inds: indices of which cell rois to get
        returns: self.traces: N x T array of cell activity
        """
        if self.all_traces is None:
            self.read_inscopix()

        if cell_inds is not None:
            return self.all_traces.values.T[cell_inds, :]
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

    def get_DLC_data(self,data = 'freezing'):

        DLC_path = os.path.join(os.path.join(self.base_dir,'Analysis','DLC'))
        ani_id = self.animal[-1]
        DLC_file = os.path.join(DLC_path,'Astro_'+ani_id+'_'+self.session.upper()+'_VideoDLC_resnet50_OLMMay26shuffle1_300000.csv')

        return DLC_file
    
    def kalman_filter_DLC(self,bparts,fps):
        dlc_file  = self.get_DLC_data()
        dlc_ = dlcResults(dlc_file)
        return dlc_.process_dlc(bparts, fps)

    def classify_cells(self):
        pass

    def event_triggered_average(self):
        pass

    # def load_registration_table(self, filter_accepted=True, session_subset=None):
    #     """
    #     session_subset: (optional) list, session indices (i.e. 0 for fc, 1 for ext1/gen1 for animal with all 5 sessions etc)
    #     to do filter accepted - maybe move this outside of the ISX class ...
    #     """
    #     if session_subset is not None:
    #         table = CellReg(self.animal, 'FOV1', N_sessions=len(session_subset),
    #                             session_inds=session_subset).load_registration_table()
    #     else:
    #         table = CellReg(self.animal, 'FOV1').load_registration_table()

    #     if filter_accepted:
    #         if self.accepted_inds is None:
    #             self.read_inscopix()

def load_registration_table(animal,session_inds,filter_accepted=True):
    cell_reg = CellReg(animal,N_sessions=len(session_inds),session_inds=session_inds)
    table = cell_reg.load_registration_table()

    if filter_accepted:
        Isx_list = [InscopixProcessing(cell_reg.animal,sess,cell_reg.base_directory) for sess in cell_reg.sessions]

        for i,ix in zip(table.columns.values,Isx_list):
            ix.read_inscopix()
            reg_cells = table.drop(cell_reg.registration_table.loc[~table[i].isin(ix.accepted_inds)].index)
    
        return reg_cells.reset_index(drop=True)
    else:
        return table

class dCA1Group:
    def __init__(self, *args):
        self.animals = {arg.animal: arg for arg in args}
        self.sessions = [arg.session  for arg in args]
        for ani, obj in self.animals.items():
            obj.read_inscopix()
        return

    def preprocess(self):
        """
        Does baseline correction and Kalman Smoothing for all cells in all the animals of the group.
        """
        print('preprocessing: detrending and smoothing')
        for ani, obj in tqdm(self.animals.items()):
            obj.apply_detrend()
            obj.apply_smoother()

    def grab_all_traces(self):
        """
        Make a single dataframe that has the accepted cells from every animal.
        """
        list_of_accepted = [ani.accepted_traces for ani in self.animals.values()]
        return pd.concat(list_of_accepted, ignore_index=True, axis=1)
    
    def save_processed_traces(self,savepath):
        list_of_accepted = [ani.accepted_traces for ani in self.animals.values()]
        print('saving preprocessed csvs')
        for session,ani,traces in tqdm(zip(self.sessions,self.animals,list_of_accepted)):
            traces.to_csv(os.path.join(savepath,ani+'_traces',ani+'_'+session+'_traces_preprocess.csv'))



# %%
