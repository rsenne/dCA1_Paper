#%%
import numpy as np
import scipy
import matplotlib.pyplot as plt

ix = onephoton.InscopixProcessing(filename='/Users/amonast/Desktop/dCA1_astro/Cell_Traces/astro5_traces/astro5_fc_traces.csv', animal='astro5')
ix.read_inscopix()
traces = ix.accepted.values

#%%
for i in range(traces.shape[1]):
    sig = traces[:,i] #isolate one cell to look at
    peaks, properties = scipy.signal.find_peaks(sig, height=np.std(sig), distance=20, width=1.4, rel_height=0.5) #height =1 std, distance = 10Hz signal is 100ms/index, so 20 is 2 seconds,
    #width = 140ms decay time for GCaMP so 1.4, rel_height = 0.5 or FWHM
    prominences = scipy.signal.peak_prominences(sig, peaks)[0]
    height = sig[peaks]-prominences
    properties #show the dictionary with the peak properties

    #
    plt.figure()
    plt.plot(sig)
    plt.plot(peaks, sig[peaks], 'x')
    plt.ylabel('dF/F')
    plt.xlabel('Time (ms)')
    plt.vlines(x=peaks, ymin=height, ymax=sig[peaks], color='orange')

    plt.savefig(f"/Users/amonast/Desktop/dCA1_astro/Figures/event detection/trial_events_fc_{i}.png")
# %%
