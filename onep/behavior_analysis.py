import pandas as pd
import numpy as np
import pykalman

__all__ = ["calculate_binned_freezing", "create_freeze_vector", "find_onset_offset", "initialize_matrices", "read_dlc_file", "kalman_filter", "calculate_centroids", "process_dlc"]


def calculate_binned_freezing(anymaze_fp,
                              bin_duration=120,
                              start=None, end=None,
                              offset=0,
                              time_format='%H:%M:%S.%f',
                              time_col='Time',
                              behavior_col='Freezing'):
    anymaze_df = pd.read_csv(anymaze_fp)
    # convert to datetimes and subtract any offset
    anymaze_df[time_col] = pd.to_datetime(anymaze_df.Time, format=time_format) - pd.Timedelta(seconds=offset)
    anymaze_df['duration'] = anymaze_df[time_col].diff().dt.total_seconds()

    # If custom_start or custom_end is None, use the first or last timestamp respectively.
    start = pd.to_datetime(start, format=time_format) if start is not None else anymaze_df[time_col].iloc[0]
    end = pd.to_datetime(end, format=time_format) if end is not None else anymaze_df[time_col].iloc[-1]

    anymaze_df['bin'] = pd.cut(anymaze_df[time_col], pd.date_range(start=start,
                                                                   end=end,
                                                                   freq=f'{bin_duration}s'))
    result = anymaze_df.groupby(['bin', behavior_col])['duration'].sum().reset_index()
    return result[result[behavior_col] == 1]


def create_freeze_vector(anymaze_fp, timestamps, time_format='%H:%M:%S.%f', time_col='Time', behavior_col='Freezing'):
    anymaze_df = pd.read_csv(anymaze_fp)
    binary_vector = np.zeros(len(timestamps), dtype=int)
    for i, ts in enumerate(timestamps):
        state = anymaze_df.loc[anymaze_df[time_col] <= ts, behavior_col].iloc[-1]
        # Get the last label before the current timestamp
        binary_vector[i] = state
    return binary_vector


def find_onset_offset(freeze_vector):
    # Calculate differences
    diff = np.diff(np.insert(np.append(freeze_vector, 0), 0, 0))  # Calculate differences
    # find offsets and offsets, difference of -1 indicates onset, 1 indicates offset
    onsets = np.where(diff == -1)[0] - 1  # subtracting 1 to get the correct index
    offsets = np.where(diff == 1)[0] - 1  # subtracting 1 to get the correct index
    return list(onsets), list(offsets)

def read_dlc_file(dlc_file):
    return pd.read_csv(dlc_file, header=[1, 2], index_col=[0])

def initialize_matrices(dt):
    """Initializes and returns the Kalman filter matrices."""
    # State transition matrix
    A = np.array([
        [1, 0, dt, 0, 0.5 * dt**2, 0],
        [0, 1, 0, dt, 0, 0.5 * dt**2],
        [0, 0, 1, 0, dt, 0],
        [0, 0, 0, 1, 0, dt],
        [0, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 1]
    ])

    # Observation matrix
    H = np.array([
        [1, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0]
    ])

    # Process noise covariance
    Q = np.eye(6)
    Q[4, 4], Q[5, 5] = dt**2, dt**2  # This is an assumption. Adjust based on system knowledge.

    return A, H, Q

def kalman_filter(x_data, y_data, dt=(1/15)):
    """Kalman filter for 2D tracking with explicit acceleration state.

    Args:
        x_data (list): x-coordinates of the data.
        y_data (list): y-coordinates of the data.
        dt (float): Time interval between successive observations.

    Returns:
        tuple: Returns the Kalman means and covariances.
    """
    A, H, Q = initialize_matrices(dt)
    R = np.diag([np.var(x_data), np.var(y_data)])

    kalman_filter = pykalman.KalmanFilter(
        transition_matrices=A, observation_matrices=H,
        transition_covariance=Q, observation_covariance=R,
        initial_state_covariance=np.eye(6) * 0.1,
        initial_state_mean=[x_data[0], y_data[0], 0, 0, 0, 0]
    )

    num_observations = len(x_data)
    kalman_means = np.zeros((6, num_observations)).T
    kalman_covs = np.zeros((6, 6, num_observations)).T

    kalman_means[0] = [x_data[0], y_data[0], 0, 0, 0, 0]
    kalman_covs[0] = np.eye(6) * 0.1

    observations = np.vstack((x_data, y_data)).T
    kalman_means, kalman_covs = kalman_filter.smooth(observations)

    return kalman_means, kalman_covs

def calculate_centroids(dlc_df):
    dlc_df.loc[:, ('centroid', 'x')] = dlc_df.xs('x', axis=1, level=1).mean(axis=1)
    dlc_df.loc[:, ('centroid', 'y')] = dlc_df.xs('y', axis=1, level=1).mean(axis=1)
    return dlc_df

def filter_predictions(dlc_df, bparts=None, fps=None):
    if bparts is None:
        bparts = bparts=["snout", 'ear_r', 'ear_l', 'shoulder_r', 'shoulder_l', 'spine_top', 'spine_mid', 'spine_bott', 'hip_l', 'hip_r', 'tail_base', 'tail_end', 'centroid']
    if fps is None:
        fps = 30

    dt = 1 / fps

    kalman_dict = {}
    for bpart in bparts:
        k_means, _ = kalman_filter(dlc_df.loc[:, (bpart, 'x')], dlc_df.loc[:, (bpart, 'y')],
                                                 dt=dt)
        kalman_dict[bpart] = {
            'x': k_means[:, 0],
            'y': k_means[:, 1],
            'velocity_x': k_means[:, 2],
            'velocity_y': k_means[:, 3],
            'acceleration_x': k_means[:, 4],
            'acceleration_y': k_means[:, 5]
        }

    reformed_dict = {}
    for outerKey, innerDict in kalman_dict.items():
        for innerKey, values in innerDict.items():
            reformed_dict[(outerKey, innerKey)] = values

    df = pd.DataFrame.from_dict(reformed_dict)
    return df

def process_dlc(dlc_df, bparts=None, fps=None):
    dlc_df = calculate_centroids(dlc_df)
    dlc_df = filter_predictions(dlc_df, bparts=bparts, fps=fps)
    return dlc_df

