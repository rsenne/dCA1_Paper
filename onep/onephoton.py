import numpy as np
import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm
import matplotlib.pyplot as plt
import pykalman
from scipy.sparse.linalg import spsolve
from scipy import sparse
from scipy.interpolate import interp1d
from joblib import Parallel, delayed
from sklearn.preprocessing import StandardScaler
import pickle as pkl
import seaborn as sns
import os
import h5py
from onep import behavior_analysis

__all__ = ["InscopixProcessing", "dCA1Group", "maxsort", "cross_validated_heat_plot", "sequence_heat_plot", "cosine_similarity_matrix"]

class InscopixProcessing():
    def __init__(self, animal, session, data_directory):
        self.base_dir = data_directory
        self.rejected_inds = None
        self.accepted_inds = None
        self.accepted_df = None
        self.CellReg_path = os.path.join(data_directory, 'CellReg')
        self.Traces_path = os.path.join(data_directory, 'Cell_Traces', animal + '_traces')
        self.Anymaze_path = os.path.join(data_directory, 'Anymaze', animal)

        if not os.path.exists(self.CellReg_path):
            raise FileNotFoundError("Could not find CellReg subfolder, check data directory & subfolders")
        if not os.path.exists(self.Traces_path):
            raise FileNotFoundError("Couldn't find Traces subfolder, check data directory & subfolders")

        self.session = session
        self.animal = animal
        self.filename = os.path.join(self.Traces_path, animal + '_' + session + '_traces.csv')
        self.all_traces = None
        self.accepted_traces = None
        self.rejected_traces = None
        self.read_inscopix()
        self.Timestamps = self.accepted_traces.index
        self.anymaze = os.path.join(self.Anymaze_path, animal + "_" + session + "_behavior.csv")
        self.binned_freezing, self.anymaze_df = behavior_analysis.calculate_binned_freezing(self.anymaze)
        self.freeze_vector = behavior_analysis.create_freeze_vector(self.anymaze_df, timestamps=self.Timestamps)
        self.onsets, self.offsets = behavior_analysis.find_onset_offset(self.freeze_vector, self.Timestamps)

    def get_registration_table(self, session_labels=["FC-HAB", "FC-A", "FC-B"]):
        """
        Loads the cell_to_index_map from the most recent CellReg output in per-session folders.
        """
        registration_tables = {}
        reg_base = os.path.join(self.base_dir, "CellReg", self.animal)
        for label in reversed(session_labels):
            session_dir = os.path.join(reg_base, f"CellRegResults{label}")
            if not os.path.exists(session_dir):
                continue
            mat_files = [f for f in os.listdir(session_dir) if "cellRegistered" in f]
            if mat_files:
                latest = sorted(mat_files)[-1]
                with h5py.File(os.path.join(session_dir, latest), "r") as file:
                    reg_map = file['cell_registered_struct']['cell_to_index_map'][()]
                    registration_tables[label] = reg_map.T.astype(int) - 1
        if registration_tables:
            self.registration_tables = registration_tables
            return registration_tables
        raise FileNotFoundError("No 'cellRegistered' file found in any session.")

    def run_behavior_analysis(self):
        self.binned_freezing, self.anymaze_df = behavior_analysis.calculate_binned_freezing(self.anymaze)
        self.freeze_vector = behavior_analysis.create_freeze_vector(self.anymaze_df, timestamps=self.Timestamps)
        self.onsets, self.offsets = behavior_analysis.find_onset_offset(self.freeze_vector, self.Timestamps)

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
        results = Parallel(n_jobs=-1)(
            delayed(self._als_detrend)(self.accepted_traces[col].values) for col in self.accepted_traces.columns)

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
        results = Parallel(n_jobs=-1)(
            delayed(self.kalman_smoother)(self.accepted_traces[col].values) for col in self.accepted_traces.columns)

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

    def eta_individual_cells(self, events=None, window=10, ax=None, **kwargs):
        data = self.accepted_traces.to_numpy()
        data = stats.zscore(data, axis=0)  # z-scored data

        # Window in seconds times 30 indices per second and half the window period to visualize before
        number_of_indices = int(window * 1.5 * 15)

        def event_interpolation(data, events_):
            interp = interp1d(self.Timestamps, data, kind='cubic')
            within_eta_ = np.zeros((len(events_), number_of_indices))
            for i, event in enumerate(events_):
                time_period = np.linspace(event - (window / 2), event + window, number_of_indices)
                within_eta_[i] = interp(time_period)
            return np.average(within_eta_, axis=0)

        across_eta_ = np.zeros((data.shape[1], number_of_indices))

        # If there's only one event, repeat it for each curve
        if len(events) == 1:
            events = events * len(data)

        for j in range(np.shape(data)[1]):
            across_eta_[j] = event_interpolation(data.transpose()[j], events[j])

        # make a figure
        if ax is None:
            fig, ax = plt.subplots(len(across_eta_), 1, sharex='col', figsize=(4, 60))

        time = np.linspace(-window / 2, window, number_of_indices)

        for i in range(data.shape[1]):
            ax[i].plot(time, np.array(across_eta_[i, :]))
            ax[i].grid(False)
            ax[i].spines['top'].set_visible(False)
            ax[i].spines['right'].set_visible(False)
            ax[i].axvline(0, linestyle='--', color='black')
            ax[i].set_ylabel(r'$\frac{dF}{F}$ (%)')
        plt.subplots_adjust(wspace=0.05)
        plt.xlabel('Time(s)')

        if ax is None:
            return fig, ax, across_eta_, time
        else:
            return ax, across_eta_, time

    def sort_cells(self):
        """
        Sorts cells by the argmax of each trace, i.e. the earliest maximum will be the first cell, etc.
        """
        # load cells
        cell_table = self.accepted_traces.to_numpy()
        # standardize cells
        ss = StandardScaler()
        cell_table = ss.fit_transform(cell_table)
        # do single event "eta's"
        pass

    def grab_all_traces(self):
        """
        Make a single dataframe that has the accepted cells from every animal.
        """
        list_of_accepted = [ani.accepted_traces for ani in self.animals.values()]
        return pd.concat(list_of_accepted, ignore_index=True, axis=1)
    
    def save_group(self, filename):
        """
        Save the object as a pickle file for later.
        """
        with open(filename, 'wb') as f:
            pkl.dump(self, f)
        return

class dCA1Group:
    def __init__(self, *args):
        self.animals = {arg.animal: arg for arg in args}
        return

    def preprocess(self):
        """
        Does baseline correction and Kalman Smoothing for all cells in all the animals of the group.
        """
        for ani, obj in self.animals.items():
            obj.apply_detrend()
            obj.apply_smoother()

    def grab_all_traces(self):
        """
        Make a single dataframe that has the accepted cells from every animal.
        """
        list_of_accepted = [ani.accepted_traces for ani in self.animals.values()]
        return pd.concat(list_of_accepted, ignore_index=True, axis=1)

    def save_group(self, filename):
        """
        Save the object as a pickle file for later.
        """
        with open(filename, 'wb') as f:
            pkl.dump(self, f)
        return


def maxsort(arr):
    """
    Sorts an array by the argmax of each row.
    """
    sorted_idxs = np.argsort(np.argmax(arr, axis=1))
    return arr[sorted_idxs], sorted_idxs

def sequence_heat_plot(unsorted_array, time, ax=None):
    """
    arr: N x T array of cell activity
    time: T array of time
    returns: ax
    """
    import matplotlib.ticker as ticker
    # z-score array
    arr = stats.zscore(unsorted_array, axis=1)
    # sort array based on argmax of each row
    arr, _ = maxsort(arr)  
    # make a figure
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=(5, 5))
    # plot the heatmap
    sns.heatmap(arr, cmap='mako',cbar=True, cbar_kws={"label": r"z-scored $\frac{dF}{F}$"})
    # set x-ticks
    ax.set_xticks(np.linspace(0, arr.shape[1], 5), np.linspace(np.min(time), np.max(time), 5))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(10))
    ax.axvline((time.shape[0]/10), linestyle='--', color='white')
    # set labels
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Cells')
    plt.tight_layout()
    return ax, fig

def cross_validated_heat_plot(unsorted_array, idxes_to_sort, sorted_array, time, ax=None):
    """_summary_

    Args:
        unsorted_array (_type_): original array
        idxes_to_sort (_type_): list of indices used to sort unsorted_array
        sorted_array (_type_): array of data sorted based on idxes_to_sort
        time (_type_): time values used for setting x-axis ticks
        ax (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    # sort array based on idxes_to_sort
    cross_valled = unsorted_array[idxes_to_sort]

    # calculate spearman correlation
    # rho, p = stats.spearmanr(cross_valled, sorted_array, axis=None)
    # print(rho, p)

    # make a figure
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=(5, 5))
    # plot the heatmap
    sns.heatmap(cross_valled, cmap='mako', cbar=True, cbar_kws={"label": r"z-scored $\frac{dF}{F}$"})
    # set x-ticks
    ax.set_xticks(np.linspace(0, cross_valled.shape[1], 5), np.linspace(np.min(time), np.max(time), 5))
    ax.axvline((time.shape[0]/3), linestyle='--', color='white')
    # set labels
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Cells')
    return ax

def cosine_similarity_matrix(arr, time, cmap, seq_times=[120, 180, 240, 300]):
    """
    arr: N x T array of cell activity
    time: array of timestamps
    returns: N x N array of cosine similarity
    """
    # Ensure time is a numpy array
    time = np.array(time)

    # first adjust all arrays to 330s
    idxs = time <= 330
    arr = arr[idxs]
    time = time[idxs]

    # gets norms
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    arr = arr / norms

    # calculates cosine similarity
    cos_sim = np.dot(arr, arr.T)

    # make a figure
    fig, ax = plt.subplots()

    # plot the heatmap
    sns.heatmap(cos_sim, cmap=cmap, cbar=True, cbar_kws={"label": "Cosine Similarity"}, rasterized=True, vmin=-1, vmax=1, ax=ax)

    # add white-dashed lines to show sequence times
    for seq_time in seq_times:
        idx = int(seq_time / 330 * len(time))
        ax.axvline(idx, linestyle='--', color='white')
        ax.axhline(idx, linestyle='--', color='white')

    # set labels
    ax.set_xlabel("Time (s)", fontsize=14)
    ax.set_ylabel("Time (s)", fontsize=14)

    # set x_ticks and y_ticks
    num_ticks = 12  # 0, 30, 60, ..., 330
    tick_locations = np.linspace(0, len(time) - 1, num_ticks).astype(int)
    tick_labels = np.linspace(0, 330, num_ticks).astype(int)
    
    ax.set_xticks(tick_locations)
    ax.set_xticklabels(tick_labels)
    ax.set_yticks(tick_locations)
    ax.set_yticklabels(tick_labels)

    return cos_sim, ax, fig