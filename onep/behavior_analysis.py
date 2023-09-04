import pandas as pd
import numpy as np

__all__ = ["calculate_binned_freezing", "create_freeze_vector"]


def calculate_binned_freezing(anymaze_df,
                                bin_duration=60,
                                start=None, end=None,
                                offset=0,
                                time_col='Time',
                                behavior_col='Freezing'):
    def __convert_time_to_seconds__(time_series):
        # Split the time and then convert to seconds
        time_data = time_series.str.split(':').tolist()
        return [int(x[0]) * 3600 + int(x[1]) * 60 + float(x[2]) for x in time_data]

    anymaze_df = pd.read_csv(anymaze_df)
    anymaze_df.Time = __convert_time_to_seconds__(anymaze_df.Time)

    # Subtract the offset directly
    anymaze_df[time_col] = anymaze_df[time_col].astype(float) - offset

    # Calculate the duration between rows
    anymaze_df['duration'] = anymaze_df[time_col].diff().fillna(0)

    # Set default start and end times if not specified
    start = start if start is not None else anymaze_df[time_col].iloc[0]
    end = end if end is not None else anymaze_df[time_col].iloc[-1]

    bins = np.arange(start, end + bin_duration, bin_duration)  # create bins
    anymaze_df['bin'] = pd.cut(anymaze_df[time_col], bins, include_lowest=True, right=False)

    # Filter rows where the behavior is freezing (i.e., behavior_col is 1)
    freezing_data = anymaze_df[anymaze_df[behavior_col] == 0]

    # Group by the bins and sum the duration
    freezing_durations = freezing_data.groupby('bin')['duration'].sum()

    # Convert to percentages
    freezing_percentages = (freezing_durations / bin_duration) * 100

    return pd.DataFrame({'bin': freezing_durations.index, 'freezing_percentage': freezing_percentages}).reset_index(
        drop=True), anymaze_df


def create_freeze_vector(anymaze_df, timestamps, time_col='Time', behavior_col='Freezing'):
    binary_vector = np.zeros(len(timestamps), dtype=int)

    for i, ts in enumerate(timestamps):
        state = anymaze_df.loc[anymaze_df[time_col] <= ts, behavior_col].iloc[-1]
        binary_vector[i] = state
    return binary_vector
