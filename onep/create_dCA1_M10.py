import tifffile
import numpy as np
import pandas as pd
import pathlib
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from tqdm import tqdm

def calculate_dff_two_segments(trace, changepoint=2643):
    """
    Calculate dF/F for a trace with a changepoint: use different baselines before and after.

    Args:
        trace (np.ndarray): 1D time series.
        changepoint (int): Frame index where signal baseline changes.
    
    Returns:
        np.ndarray: Combined dF/F trace across both segments.
    """
    pre = trace[:changepoint]
    post = trace[changepoint:]

    mean_pre = np.mean(pre) if np.mean(pre) != 0 else 1.0
    mean_post = np.mean(post) if np.mean(post) != 0 else 1.0

    dff_pre = (pre - mean_pre) / mean_pre
    dff_post = (post - mean_post) / mean_post

    return np.concatenate([dff_pre, dff_post])

def pad_footprint(footprint, pad_top=5, pad_bottom=3, pad_left=3, pad_right=10):
    """
    Pad a 2D footprint image to align with a larger DFF image.

    Args:
        footprint (np.ndarray): 2D array of the footprint image.
        pad_top, pad_bottom, pad_left, pad_right (int): Number of pixels to pad.
    
    Returns:
        np.ndarray: Padded footprint of shape matching the DFF image.
    """
    return np.pad(
        footprint,
        ((pad_top, pad_bottom), (pad_left, pad_right)),
        mode='constant',
        constant_values=0
    )

def process_footprint(foot, dff):
    """
    Process a single cell's footprint: apply spatial mask to the dF/F movie, extract and normalize the trace.

    Args:
        foot (pathlib.Path): Path to the footprint TIFF file.
        dff (np.ndarray): 3D tifffile containing the full field-of-view dF/F signal.
    
    Returns:
        tuple: (cell_label, dff_trace) where cell_label is 'CXXX' and dff_trace is a 1D np.ndarray or None
    """
    raw_id = foot.name.split("_")[3].replace(".tiff", "")
    cell_id = raw_id.lstrip("C")  # remove any leading C
    cell_label = f"C{cell_id.zfill(3)}"

    try:
        footprint = tifffile.imread(foot)
        footprint = pad_footprint(footprint)
        footprint = (footprint * 10).astype(dff.dtype)  # Convert 0.1 to 1.0

        if footprint.sum() == 0:
            return cell_label, None  # Skip if footprint is empty

        masked = dff * footprint[np.newaxis, :, :]
        trace = masked.sum(axis=(1, 2)) / footprint.sum()
        dff_trace = calculate_dff_two_segments(trace)

        return cell_label, dff_trace

    except Exception as e:
        print(f"Error processing {foot.name}: {e}")
        return cell_label, None

def create_traces(dff, footies, output_dir, output_filename="M10_FC_traces.csv"):
    """
    Create individual cell traces from the footprint files. This function loops through each footprint file,
    multiplies the tiff footprint by the dF/F file (effectively masking all irrelevant info), then calculates the dF/F for each footprint.
    We then create a pandas DataFrame in the typical Inscopix format and save it to the output directory.

    This version runs in parallel to accelerate processing.

    Args:
        dff (np.ndarray): 3D tifffile containing the dF/F movie for the session.
        footies (list): List of footprint TIFF files.
        output_dir (pathlib.Path): Directory to save the output traces.
        output_filename (str): Name of the CSV file to save.
    
    Returns: 
        pathlib.Path: Path to the saved output CSV file.
    """
    time_vector = np.round(np.linspace(0, 360, dff.shape[0]), 8)
    trace_dict = {"": ["Time(s)/Cell Status"] + time_vector.tolist()}

    with ProcessPoolExecutor() as executor:
        results = list(tqdm(
            executor.map(partial(process_footprint, dff=dff), footies),
            total=len(footies),
            desc="Processing footprints"
        ))

    for cell_label, trace in results:
        if trace is not None:
            trace_dict[cell_label] = ["accepted"] + trace.tolist()

    # print(f"Columns in trace_dict: {list(trace_dict.keys())}")

    ordered_keys = [""] + sorted(
        [k for k in trace_dict.keys() if k.startswith("C") and k[1:].isdigit()],
        key=lambda x: int(x[1:])
    )

    df_out = pd.DataFrame({k: trace_dict[k] for k in ordered_keys})
    output_path = output_dir / output_filename
    df_out.to_csv(output_path, index=False)

    return output_path

if __name__ == "__main__":
    from pathlib import Path
    import tifffile

    footprints = Path(r"Z:\Home\rsenne\CellReg\M10\FC")
    output_dir = Path(r"Z:\Home\rsenne\Cell_Traces\M10_traces")
    dff_file = Path(r"Z:\Home\rsenne\dCA1_M10\M10_FC_spatialbandpass.tiff")

    # Load files
    footies = [f for f in footprints.iterdir() if f.suffix == '.tiff' and "C" in f.name.split("_")[3]]
    dff = tifffile.imread(dff_file)

    # Call the function
    output_path = create_traces(dff, footies, output_dir)
    print(f"Saved traces to: {output_path}")