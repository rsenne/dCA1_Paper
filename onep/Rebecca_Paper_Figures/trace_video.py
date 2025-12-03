#%%
import pickle
# Load the pickle file
with open('/Users/suthardr/Desktop/collection_fc_allmice.pkl', 'rb') as file:
    collection_fc = pickle.load(file)
#%%
traces = collection_fc.animals['astroF9'].accepted_traces.to_numpy()
traces = traces[:3303, :].T
#%%
import matplotlib
# Use a non-interactive backend to avoid the backend_interagg issue
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from moviepy import VideoFileClip, VideoClip


video_path = "/Users/suthardr/Desktop/video_fc/Astro_F9_FC.avi"
output_path = "astro_F9_synced.mp4"
traces_fs = 10

n_traces_to_show = 100

n_cells, n_timepoints = traces.shape
time = np.arange(n_timepoints) / traces_fs

# --------------------------------------------------------
# Load behavior video with MoviePy
# --------------------------------------------------------
clip = VideoFileClip(video_path)
beh_fps = clip.fps
beh_duration = clip.duration

print(f"Video loaded: duration={beh_duration:.2f}s, fps={beh_fps:.2f}")

# We can only show the portion where we have both video and traces
max_time_traces = time[-1]
duration = min(beh_duration, max_time_traces)
print(f"Using duration={duration:.2f}s to sync video and traces")

# --------------------------------------------------------
# Prepare traces to plot
# --------------------------------------------------------
# Pick high-variance cells
cell_vars = traces.var(axis=1)
idx = np.argsort(cell_vars)[::-1][:min(n_traces_to_show, n_cells)]
tr_sel = traces[idx]

# Z-score each trace
tr_sel = (tr_sel - tr_sel.mean(axis=1, keepdims=True)) / (
    tr_sel.std(axis=1, keepdims=True) + 1e-9
)

# Vertical offsets so they don't overlap
tr_plot = tr_sel + np.arange(tr_sel.shape[0])[:, None]

# Precompute y-limits
y_min = -1
y_max = tr_plot.shape[0] + 1

# --------------------------------------------------------
# Function to render one frame at time t (in seconds)
# --------------------------------------------------------
def make_frame(t):
    """
    MoviePy will call this with time t (in seconds).
    We:
      - grab the video frame at time t
      - render a matplotlib figure with video + traces + red cursor
      - return it as a numpy uint8 image
    """
    # Get behavior frame at time t
    frame = clip.get_frame(t)  # shape (H, W, 3)

    # Map time t -> trace index
    trace_idx = int(t * traces_fs)
    trace_idx = np.clip(trace_idx, 0, n_timepoints - 1)

    # Create figure (non-interactive backend, off-screen)
    fig = plt.figure(figsize=(8, 6), dpi=120)
    gs = fig.add_gridspec(2, 1, height_ratios=[1, 2])
    ax_video = fig.add_subplot(gs[0, 0])
    ax_traces = fig.add_subplot(gs[1, 0])

    # --- Top: behavior video frame ---
    ax_video.imshow(frame)
    ax_video.axis("off")
    ax_video.set_title("Behavior")

    # --- Bottom: traces with red time cursor ---
    for trace in tr_plot:
        ax_traces.plot(time, trace, lw=0.3, alpha=0.25, color="black")

    # Red time cursor
    ax_traces.axvline(time[trace_idx], color="red", lw=1)

    ax_traces.set_xlim(0, time[-1])
    ax_traces.set_ylim(y_min, y_max)
    ax_traces.set_xlabel("Time (s)")
    ax_traces.set_ylabel("Cell (offset)")

    fig.tight_layout()

    # Draw to an RGB array
    fig.canvas.draw()
    w, h = fig.canvas.get_width_height()
    img = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
    img = img.reshape(h, w, 3)

    plt.close(fig)  # free memory

    return img

# --------------------------------------------------------
# Build the video with MoviePy
# --------------------------------------------------------
new_clip = VideoClip(make_frame, duration=duration)
new_clip.write_videofile(
    output_path,
    fps=beh_fps,
    codec="libx264",
    audio=False,
    preset="medium"
)

clip.close()
new_clip.close()

print(f"Saved synced video to: {output_path}")
