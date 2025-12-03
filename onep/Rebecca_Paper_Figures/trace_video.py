#%%

import pickle
with open('/Users/suthardr/Desktop/collection_fc_allmice.pkl', 'rb') as f:
    collection_fc = pickle.load(f)

#%%
traces = collection_fc.animals['astroF9'].accepted_traces.to_numpy()
traces = traces[:3603, :].T
#%% KEEP THIS
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")   # offscreen rendering
import matplotlib.pyplot as plt
from moviepy.editor import VideoFileClip

behavior_video_path = "/Users/suthardr/Desktop/video_fc/Astro_F9_FC.avi"
output_dir = "/Users/suthardr/Desktop/png_frames_fc_3603"

fs = 10.0               # calcium sampling rate
n_show = 291            # number of cells to show
t_start = 115.0          # calcium window start (s)
t_end   = 135.0         # calcium window end (s)

anchor_ca_time   = 120.0 #when should this be happening
anchor_beh_frame = 1803 #where is the first shock in the video (F9)

n_cells, n_timepoints = traces.shape
time_ca = np.arange(n_timepoints) / fs

# Calcium window
t_start = max(t_start, 0.0)
t_end = min(t_end, float(time_ca[-1]))

print(f"Calcium duration = {time_ca[-1]:.2f} s")
print(f"Rendering calcium window: {t_start:.2f}–{t_end:.2f} s")

# Select highest-variance cells
# vars_ = traces.var(axis=1)
# order = np.argsort(vars_)[::-1]
# sel = order[:min(n_show, n_cells)]
# tr = traces[sel]

#NEW#####################
event_time = 120.0  # or whatever the calcium time is
event_idx = int(round(event_time * fs))
event_idx = np.clip(event_idx, 0, n_timepoints - 1)

# Sort cells by their value at that frame (descending)
values_at_event = traces[:, event_idx]
order = np.argsort(values_at_event)[::-1]  # largest first

sel = order[:min(n_show, n_cells)]
tr = traces[sel]

window_radius = 50  # frames on each side → ~0.5 s at 10 Hz
lo = max(event_idx - window_radius, 0)
hi = min(event_idx + window_radius + 1, n_timepoints)

# use the max in that window for each cell
peaks = traces[:, lo:hi].max(axis=1)
order = np.argsort(peaks)[::-1]

sel = order[:min(n_show, n_cells)]
tr = traces[sel]
########

# Z-score & vertical offset
tr = (tr - tr.mean(axis=1, keepdims=True)) / (tr.std(axis=1, keepdims=True) + 1e-9)
offsets = np.arange(tr.shape[0])[:, None]
tr_plot = tr + offsets

ymin, ymax = -1, tr_plot.shape[0] + 1


# LOAD BEHAVIOR VIDEO

clip = VideoFileClip(behavior_video_path)
beh_fps = clip.fps
beh_duration = clip.duration
n_beh_frames = int(round(beh_fps * beh_duration))

print(f"Behavior video: {beh_duration:.2f} s, fps = {beh_fps}, ~{n_beh_frames} frames")

# FRAME-BASED ALIGNMENT
duration = t_end - t_start
n_frames = int(round(duration * beh_fps))

# index k where calcium time ~ anchor_ca_time
k_anchor = int(round((anchor_ca_time - t_start) * beh_fps))
print(f"k_anchor (for ca t={anchor_ca_time}s) ≈ {k_anchor}")

# frame offset so that beh_frame(k_anchor) = anchor_beh_frame
offset_frames = anchor_beh_frame - k_anchor
print(f"Using offset_frames = {offset_frames} (beh_frame = k + offset_frames)")

# OUTPUT DIRECTORY
os.makedirs(output_dir, exist_ok=True)

# GENERATE PNG FRAMES
for k in range(n_frames):
    t_ca = t_start + k / beh_fps
    if t_ca > t_end:
        break

    # calcium index
    idx_ca = int(round(t_ca * fs))
    idx_ca = np.clip(idx_ca, 0, n_timepoints - 1)

    # behavior frame index with offset
    beh_frame_idx = k + offset_frames
    beh_frame_idx = int(np.clip(beh_frame_idx, 0, n_beh_frames - 1))

    # behavior time for that frame
    t_beh = beh_frame_idx / beh_fps

    # get behavior frame
    frame = clip.get_frame(t_beh)

    # build figure
    fig = plt.figure(figsize=(8, 6), dpi=120)
    gs = fig.add_gridspec(2, 1, height_ratios=[1, 2])

    ax_vid = fig.add_subplot(gs[0])
    ax_tr  = fig.add_subplot(gs[1])

    # Top panel: behavior
    ax_vid.imshow(frame)
    ax_vid.axis("off")
    ax_vid.set_title(f"Behavior frame {beh_frame_idx} | Ca t = {t_ca:.2f}s")

    # Bottom panel: traces
    for y in tr_plot:
        ax_tr.plot(time_ca, y, lw=0.3, alpha=0.25, color="black")

    ax_tr.axvline(time_ca[idx_ca], color="red", lw=1)

    ax_tr.set_xlim(t_start, t_end)
    ax_tr.set_ylim(ymin, ymax)
    ax_tr.set_xlabel("Time (s)")
    ax_tr.set_ylabel("Cells (offset)")

    fig.tight_layout()

    # save PNG
    out_name = os.path.join(output_dir, f"frame_{k:05d}.png")
    fig.savefig(out_name, dpi=120)
    plt.close(fig)

    if k % 50 == 0:
        print(f"Saved frame {k}/{n_frames}")

clip.close()
print("Finished saving PNG frames.")

#%%
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")   # offscreen rendering for PNGs
import matplotlib.pyplot as plt
from moviepy.editor import VideoFileClip

behavior_video_path = "/Users/suthardr/Desktop/video_fc/Astro_F9_FC.avi"
output_dir = "/Users/suthardr/Desktop/png_frames_fc_f9"

fs = 10.0               # calcium sampling rate (Hz)
t_start = 115.0          # calcium start time (sec)
t_end   = 195.0         # calcium end time (sec)

# calcium time 120 s should correspond to behavior frame 1803
anchor_ca_time   = 120.0
anchor_beh_frame = 1803

n_cells, n_timepoints = traces.shape
time_ca = np.arange(n_timepoints) / fs

# Clamp calcium window
t_start = max(t_start, 0.0)
t_end = min(t_end, float(time_ca[-1]))

print(f"Calcium duration = {time_ca[-1]:.2f} s")
print(f"Rendering calcium window: {t_start:.2f}–{t_end:.2f} s")

# Peak time (argmax index) for each cell
peak_times = np.argmax(traces, axis=1)

# Sort ascending = early-peaking cells at top
order = np.argsort(peak_times[:])[::-1]
tr = traces[order]

# Z-SCORE + VERTICAL OFFSETS
tr = (tr - tr.mean(axis=1, keepdims=True)) / (tr.std(axis=1, keepdims=True) + 1e-9)
offsets = np.arange(tr.shape[0])[:, None]
tr_plot = tr + offsets

ymin, ymax = -1, tr_plot.shape[0] + 1

# LOAD BEHAVIOR VIDEO
clip = VideoFileClip(behavior_video_path)
beh_fps = clip.fps
beh_duration = clip.duration
n_beh_frames = int(round(beh_fps * beh_duration))

print(f"Behavior video: {beh_duration:.2f} s, fps = {beh_fps}, ~{n_beh_frames} frames")

# FRAME-BASED ALIGNMENT
# Output frame index k corresponds to:
#     calcium time: t_ca = t_start + k / beh_fps
# Anchor condition:
#     t_ca = 120 s  <--→ behavior_frame = 842
#
# k_anchor = (anchor_ca_time - t_start) * beh_fps
# beh_frame(k) = k + offset_frames
# offset_frames = anchor_beh_frame - k_anchor

duration = t_end - t_start
n_frames = int(round(duration * beh_fps))

k_anchor = int(round((anchor_ca_time - t_start) * beh_fps))
offset_frames = anchor_beh_frame - k_anchor

print(f"k_anchor = {k_anchor}")
print(f"offset_frames = {offset_frames}")

#Output
os.makedirs(output_dir, exist_ok=True)

# GENERATE PNG FRAMES
for k in range(n_frames):
    t_ca = t_start + k / beh_fps
    if t_ca > t_end:
        break

    # Calcium index
    idx_ca = int(round(t_ca * fs))
    idx_ca = np.clip(idx_ca, 0, n_timepoints - 1)

    # Behavior frame index after alignment
    beh_frame_idx = k + offset_frames
    beh_frame_idx = int(np.clip(beh_frame_idx, 0, n_beh_frames - 1))

    # Get behavior time for this frame
    t_beh = beh_frame_idx / beh_fps

    # Fetch behavior frame
    frame = clip.get_frame(t_beh)

    # ----- BUILD FIGURE -----
    fig = plt.figure(figsize=(8, 6), dpi=120)
    gs = fig.add_gridspec(2, 1, height_ratios=[1, 2])

    ax_vid = fig.add_subplot(gs[0])
    ax_tr  = fig.add_subplot(gs[1])

    # Top: behavior frame
    ax_vid.imshow(frame)
    ax_vid.axis("off")
    ax_vid.set_title(f"Behavior frame {beh_frame_idx} | t={t_ca:.2f}s")

    # Bottom: sorted traces
    for y in tr_plot:
        ax_tr.plot(time_ca, y, lw=0.3, alpha=0.25, color="black")

    # Red cursor
    ax_tr.axvline(time_ca[idx_ca], color="red", lw=1)

    # Limits
    ax_tr.set_xlim(t_start, t_end)
    ax_tr.set_ylim(ymin, ymax)
    ax_tr.set_xlabel("Time (s)")
    ax_tr.set_ylabel("Cells (sorted by peak time)")

    fig.tight_layout()

    # Save PNG
    out_path = os.path.join(output_dir, f"frame_{k:05d}.png")
    fig.savefig(out_path, dpi=120)
    plt.close(fig)

    if k % 50 == 0:
        print(f"Saved frame {k}/{n_frames}")

clip.close()
print("Finished saving PNG frames.")
#%%
 cd /Users/suthardr/Desktop/png_frames_fc
ffmpeg -framerate 14 -i frame_%05d.png -vcodec mpeg4 -q:v 2 ../Astro_F9_FC_synced.mp4
#%%THSI WORKS 
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")   # offscreen rendering for PNGs
import matplotlib.pyplot as plt
from moviepy.editor import VideoFileClip

# --------------------------------------------------
# USER SETTINGS
# --------------------------------------------------

behavior_video_path = "/Users/suthardr/Desktop/video_fc/Astro_F9_FC.avi"
output_dir = "/Users/suthardr/Desktop/png_frames_fc_115_195_ratio"

fs = 10.0          # calcium sampling rate (Hz)
t_start = 115.0    # calcium window start (s)
t_end   = 195.0    # calcium window end (s)

# --------------------------------------------------
# PREP CALCIUM TRACES
# --------------------------------------------------

print("Original traces shape:", traces.shape)

# Ensure shape is (cells, frames)
if traces.shape[0] == 3603 and traces.shape[1] != 3603:
    traces = traces.T
    print("Transposed traces:", traces.shape)

n_cells, n_timepoints = traces.shape
time_ca = np.arange(n_timepoints) / fs

# Clamp window
t_start = max(t_start, 0.0)
t_end = min(t_end, float(time_ca[-1]))

print(f"Using calcium window: {t_start}–{t_end} s")

# --------------------------------------------------
# SORT CELLS BY ARGMAX (ASCENDING)
# --------------------------------------------------

peak_times = np.argmax(traces, axis=1)   # peak index for each cell
order_cells = np.argsort(peak_times)     # earliest peaks at top
tr = traces[order_cells]

# Z-score + vertical offsets
tr = (tr - tr.mean(axis=1, keepdims=True)) / (tr.std(axis=1, keepdims=True) + 1e-9)
offsets = np.arange(tr.shape[0])[:, None]
tr_plot = tr + offsets

ymin, ymax = -1, tr_plot.shape[0] + 1

# --------------------------------------------------
# LOAD BEHAVIOR VIDEO
# --------------------------------------------------

clip = VideoFileClip(behavior_video_path)
beh_fps = clip.fps     # only for MoviePy timing
beh_duration = clip.duration

print(f"Behavior duration = {beh_duration:.2f} s (reported fps = {beh_fps})")

# --------------------------------------------------
# FRAME-RATIO ALIGNMENT: PURE LINEAR
#
# trace_frame → video_frame = round( trace_idx * (5402 / 3602) )
# --------------------------------------------------

N_trace = 3603
N_video = 5403

RATIO = (N_video - 1) / (N_trace - 1)   # = 5402 / 3602
print(f"Using frame ratio: {RATIO:.6f} (video frames per trace frame)")

# Number of PNG frames to generate: drive using the video frame rate
duration = t_end - t_start
n_frames = int(round(duration * beh_fps))
print(f"Will render {n_frames} PNG frames")

# --------------------------------------------------
# OUTPUT DIRECTORY
# --------------------------------------------------

os.makedirs(output_dir, exist_ok=True)

# --------------------------------------------------
# GENERATE PNG FRAMES
# --------------------------------------------------

for k in range(n_frames):

    # calcium time for this PNG
    t_ca = t_start + k / beh_fps
    if t_ca > t_end:
        break

    # calcium frame index
    trace_idx = int(round(t_ca * fs))
    trace_idx = np.clip(trace_idx, 0, N_trace - 1)

    # video frame index by pure ratio
    video_idx = int(round(trace_idx * RATIO))
    video_idx = np.clip(video_idx, 0, N_video - 1)

    # convert video frame index → time for MoviePy
    t_beh = video_idx / beh_fps
    t_beh = float(np.clip(t_beh, 0, beh_duration))

    # fetch video frame
    frame = clip.get_frame(t_beh)

    # ----- PLOT -----
    fig = plt.figure(figsize=(8, 6), dpi=120)
    gs = fig.add_gridspec(2, 1, height_ratios=[1, 2])

    ax_vid = fig.add_subplot(gs[0])
    ax_tr  = fig.add_subplot(gs[1])

    # Top: behavior frame
    ax_vid.imshow(frame)
    ax_vid.axis("off")
    ax_vid.set_title(f"Video frame {video_idx} | Beh t={t_beh:.2f}s | Ca t={t_ca:.2f}s")

    # Bottom: sorted traces
    ax_tr.plot(time_ca, tr_plot.T, lw=0.3, alpha=0.25, color="black")

    # Cursor
    ax_tr.axvline(time_ca[trace_idx], color="red", lw=1)

    ax_tr.set_xlim(t_start, t_end)
    ax_tr.set_ylim(ymin, ymax)
    ax_tr.set_xlabel("Calcium time (s)")
    ax_tr.set_ylabel("Cells (sorted by argmax time)")

    fig.tight_layout()

    # Save PNG
    out_path = os.path.join(output_dir, f"frame_{k:05d}.png")
    fig.savefig(out_path, dpi=120)
    plt.close(fig)

    if k % 50 == 0:
        print(f"Saved frame {k}/{n_frames}")

clip.close()
print("Finished saving PNG frames (115–195 s, ratio-aligned).")
