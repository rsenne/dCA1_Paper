import pandas as pd
import numpy as np

__all__ = ["calculate_binned_freezing", "create_freeze_vector"]


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
