#%%

import pickle
with open('/Users/suthardr/Desktop/collection_fc_allmice.pkl', 'rb') as f:
    collection_fc = pickle.load(f)

#%%
traces = collection_fc.animals['astroF9'].accepted_traces.to_numpy()
traces = traces[:3603, :].T
#%%
 cd /Users/suthardr/Desktop/Revision/video_cxtb/CxtB_F9_behavior
ffmpeg -framerate 14 -i frame_%05d.png -vcodec mpeg4 -q:v 2 ../Astro_F9_CxtB_behavior.mp4
#%%THSI WORKS
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")   # offscreen rendering for PNGs
import matplotlib.pyplot as plt
from moviepy.editor import VideoFileClip

behavior_video_path = "/Users/suthardr/Desktop/video_cxta/F9_CxtA_03192025_Day1.avi"
output_dir = "/Users/suthardr/Desktop/video_cxta/CxtA_F9"

fs = 10.0          # calcium sampling rate (Hz)
t_start = 90.0    # calcium window start (s)
t_end   = 165.0    # calcium window end (s)

n_cells, n_timepoints = traces.shape
time_ca = np.arange(n_timepoints) / fs

# Clamp window
t_start = max(t_start, 0.0)
t_end = min(t_end, float(time_ca[-1]))

print(f"Using calcium window: {t_start}–{t_end} s")

# SORT CELLS BY ARGMAX (ASCENDING)
peak_times = np.argmax(traces, axis=1)   # peak index for each cell
order_cells = np.argsort(peak_times)[::-1]
tr = traces[order_cells]

# Z-score + vertical offsets
tr = (tr - tr.mean(axis=1, keepdims=True)) / (tr.std(axis=1, keepdims=True) + 1e-9)
offsets = np.arange(tr.shape[0])[:, None]
tr_plot = tr + offsets

ymin, ymax = -1, tr_plot.shape[0] + 1

# LOAD BEHAVIOR VIDEO
clip = VideoFileClip(behavior_video_path)
beh_fps = clip.fps
beh_duration = clip.duration

print(f"Behavior duration = {beh_duration:.2f} s (reported fps = {beh_fps})")

# FRAME-RATIO ALIGNMENT:
N_trace = 3603 #frames in the trace file
N_video = 5403 #frames in the video (.avi)

RATIO = (N_video - 1) / (N_trace - 1)
print(f"Using frame ratio: {RATIO:.6f} (video frames per trace frame)")

# Number of PNG frames to generate
duration = t_end - t_start
n_frames = int(round(duration * beh_fps))
print(f"Will render {n_frames} PNG frames")

# OUTPUT DIRECTORY
os.makedirs(output_dir, exist_ok=True)

# GENERATE PNG FRAMES
for k in range(n_frames):

    # calcium time for this PNG
    t_ca = t_start + k / beh_fps
    if t_ca > t_end:
        break

    # calcium frame index
    trace_idx = int(round(t_ca * fs))
    trace_idx = np.clip(trace_idx, 0, N_trace - 1)

    # video frame index by ratio
    video_idx = int(round(trace_idx * RATIO))
    video_idx = np.clip(video_idx, 0, N_video - 1)

    # convert video frame index → time
    t_beh = video_idx / beh_fps
    t_beh = float(np.clip(t_beh, 0, beh_duration))

    # fetch video frame
    frame = clip.get_frame(t_beh)

    # ----- PLOT -----
    fig = plt.figure(figsize=(8, 6), dpi=120)
    gs = fig.add_gridspec(2, 1, height_ratios=[1, 2])

    ax_vid = fig.add_subplot(gs[0])
    ax_tr  = fig.add_subplot(gs[1])
    ax_tr.axvline(98.53078008, color="black", lw=1, linestyle="--")
    ax_tr.axvline(144.394920, color="black", lw=1, linestyle="--")

    # Top: behavior frame
    ax_vid.imshow(frame)
    ax_vid.axis("off")
    #ax_vid.set_title(f"Video frame {video_idx} | Behavior t={t_beh:.2f}s | Calcium t={t_ca:.2f}s")
    ax_vid.set_title(f"Time={t_ca:.2f}s")

    # Bottom: sorted traces
    ax_tr.plot(time_ca, tr_plot.T, lw=0.7, alpha=0.25, color="black")

    # Cursor
    ax_tr.axvline(time_ca[trace_idx], color="red", lw=1)

    ax_tr.set_xlim(t_start, t_end)
    ax_tr.set_ylim(ymin, ymax)
    ax_tr.set_xlabel("Time (s)")
    ax_tr.set_ylabel("Cells (sorted by argmax)")

    fig.tight_layout()

    # Save PNG
    out_path = os.path.join(output_dir, f"frame_{k:05d}.png")
    fig.savefig(out_path, dpi=120)
    plt.close(fig)

    if k % 50 == 0:
        print(f"Saved frame {k}/{n_frames}")

clip.close()
print("Finished saving PNG frames")
#%%
import matplotlib.pyplot as plt

animal = collection_fc.animals['astroF9']

time = animal.Timestamps          # or animal.t
freeze = animal.freeze_vector      # your binary freezing signal

plt.figure(figsize=(12, 4))
plt.step(time, freeze, where='post')

plt.xlabel("Time (s)")
plt.ylabel("Freezing (0/1)")
plt.title("Freezing Behavior Over Time — astroF9")
plt.ylim(-0.1, 1.1)

out_path = os.path.join(output_dir, f"freezing_f9_cxta.png")
plt.savefig(out_path, dpi=120)
plt.close(fig)

#%%Plot behavior with the video trace thign
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")   # offscreen rendering for PNGs
import matplotlib.pyplot as plt
from moviepy.editor import VideoFileClip

behavior_video_path = "/Users/suthardr/Desktop/video_fc/Astro_F9_FC.avi"
output_dir = "/Users/suthardr/Desktop/video_fc/png_frames_fc_F9_behavior"

fs = 10.0          # calcium sampling rate (Hz)
t_start = 115.0     # calcium window start (s)
t_end   = 195.0    # calcium window end (s)

# -----------------------------------------------------------
#             LOAD CALCIUM DATA INTO traces, time_ca
# -----------------------------------------------------------
n_cells, n_timepoints = traces.shape
time_ca = np.arange(n_timepoints) / fs

# clamp window to available data
t_start = max(t_start, 0)
t_end   = min(t_end, float(time_ca[-1]))

print(f"Using calcium window: {t_start}–{t_end} s")

# -------------------- SORT CELLS --------------------------
peak_times = np.argmax(traces, axis=1)
order_cells = np.argsort(peak_times)[::-1]
tr = traces[order_cells]

# z-score + offsets
tr = (tr - tr.mean(axis=1, keepdims=True)) / (tr.std(axis=1, keepdims=True) + 1e-9)
offsets = np.arange(tr.shape[0])[:, None]
tr_plot = tr + offsets

ymin, ymax = -1, tr_plot.shape[0] + 1

# -----------------------------------------------------------
#                 LOAD FREEZING DATA
# -----------------------------------------------------------
animal = collection_fc.animals['astroF9']
time_freeze = np.asarray(animal.Timestamps, dtype=float)
freeze      = np.asarray(animal.freeze_vector, dtype=float)

# slice to window
mask = (time_freeze >= t_start) & (time_freeze <= t_end)
time_freeze_win = time_freeze[mask]
freeze_win      = freeze[mask]

print(f"Freezing samples inside window: {time_freeze_win.size}")

# -----------------------------------------------------------
#                 LOAD BEHAVIOR VIDEO
# -----------------------------------------------------------
clip = VideoFileClip(behavior_video_path)
beh_fps = clip.fps
beh_duration = clip.duration
print(f"Behavior duration = {beh_duration:.2f} s, FPS = {beh_fps}")

# ------------------ TRACE ↔ VIDEO ALIGNMENT ----------------
N_trace = 3603  # number of trace frames
N_video = 5403  # number of video frames

RATIO = (N_video - 1) / (N_trace - 1)
print(f"Frame ratio (video per trace) = {RATIO:.6f}")

# number of output PNG frames
duration = t_end - t_start
n_frames = int(round(duration * beh_fps))
print(f"Will generate {n_frames} PNG frames")

# ===========================================================
#                  MAIN FRAME GENERATION LOOP
# ===========================================================
for k in range(n_frames):

    # calcium time for this PNG
    t_ca = t_start + k / beh_fps
    if t_ca > t_end:
        break

    # calcium frame index
    trace_idx = int(round(t_ca * fs))
    trace_idx = np.clip(trace_idx, 0, N_trace - 1)

    # video frame index
    video_idx = int(round(trace_idx * RATIO))
    video_idx = np.clip(video_idx, 0, N_video - 1)

    # convert index to behavior timestamp
    t_beh = float(np.clip(video_idx / beh_fps, 0, beh_duration))

    # video frame
    frame = clip.get_frame(t_beh)

    # =======================================================
    #                FIGURE LAYOUT
    #       [ VIDEO ]          <-- big
    #       [ FREEZE RIBBON ]  <-- thin, despined
    #       [ TRACES ]         <-- big, with x-axis
    # =======================================================
    fig = plt.figure(figsize=(8, 7), dpi=120)
    gs = fig.add_gridspec(3, 1, height_ratios=[3, 0.4, 3])

    # create trace axis first so freeze can share x-axis
    ax_tr = fig.add_subplot(gs[2])
    ax_vid = fig.add_subplot(gs[0])
    ax_freeze = fig.add_subplot(gs[1], sharex=ax_tr)

    # ---------------- VIDEO (top) ----------------
    ax_vid.imshow(frame)
    ax_vid.axis("off")
    ax_vid.set_title(f"Time = {t_ca:.2f}s")

    # ---------------- FREEZING RIBBON (middle) ----------------
    ax_freeze.fill_between(
        time_freeze_win,
        0,
        freeze_win,
        step="post",
        alpha=0.5,
        color="black"
    )
    ax_freeze.axvline(t_ca, color="red", lw=1)

    # ribbon look: no y-label, no ticks, no spines, no x-axis
    ax_freeze.set_ylim(-0.1, 1.1)
    ax_freeze.set_yticks([])
    ax_freeze.set_ylabel("")
    ax_freeze.tick_params(
        axis="both",
        which="both",
        bottom=False,
        top=False,
        left=False,
        labelbottom=False,
        labelleft=False,
    )
    for spine in ax_freeze.spines.values():
        spine.set_visible(False)

    # ---------------- CALCIUM TRACES (bottom) ----------------
    ax_tr.plot(time_ca, tr_plot.T, lw=0.7, alpha=0.25, color="black")

    # event markers (if you want them)
    ax_tr.axvline(120, color="black", lw=1, linestyle="--")
    ax_tr.axvline(180,  color="black", lw=1, linestyle="--")

    # time cursor
    ax_tr.axvline(time_ca[trace_idx], color="red", lw=1)

    ax_tr.set_xlim(t_start, t_end)
    ax_tr.set_ylim(ymin, ymax)
    ax_tr.set_xlabel("Time (s)")
    ax_tr.set_ylabel("Cells (sorted by argmax)")

    fig.tight_layout()

    # save
    out_path = os.path.join(output_dir, f"frame_{k:05d}.png")
    fig.savefig(out_path, dpi=120)
    plt.close(fig)

    if k % 50 == 0:
        print(f"Saved frame {k}/{n_frames}")

clip.close()
print("Finished saving PNG frames with video + freezing ribbon + traces.")