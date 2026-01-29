from scipy.stats import zscore
import onep.onephoton as onep
from onep.Finalized.trace_analysis_functions import eta_individual_cells
import numpy as np
import seaborn as sb
import matplotlib as mpl
import matplotlib.pyplot as plt



def main(animal):
#FC traces 
    animal = animal
    astro = onep.InscopixProcessing(session='fc', animal=animal, data_directory='/Users/suthardr/Desktop/')
    session_ind = 0
    collection = onep.dCA1Group(astro)
    fc_traces = collection.grab_all_traces().to_numpy().T

    foots=astro.load_footprints(session_subset=[0])
    footies = foots[session_ind][astro.accepted_inds]
    plt.imshow(footies.max(axis=0))
    plt.show() # initial footprints

    # Generate ETA sequence for session; Sorted by argmax
    timestamps = astro.Timestamps[0:3303]
    fc_ctxa_traces_z = zscore(fc_traces[:,0:3303], axis=1)
    ax1,across_eta,time=eta_individual_cells(data=fc_ctxa_traces_z, timestamps=timestamps[:3303], events=[[120,180,240,300], ], window=28)
    max_indices = np.argmax(across_eta, axis=1)
    time = np.linspace(-14, 28, 5)
    sorted_ind = np.argsort(max_indices)
    sorted_arr = across_eta[sorted_ind]
    fig1, ax1 = plt.subplots()
    sb.heatmap(sorted_arr, cbar=True, cmap='Greys', cbar_kws={"label": r"z-scored $\frac{dF}{F}$"})
    ax1.set_xticks(np.linspace(0, len(across_eta.T), 5), time)
    ax1.set_title('FC: Astro dCA1 Shock #1')
    ax1.set_xlabel('Time (seconds)')
    plt.show()

    if footies.shape[0]!=fc_ctxa_traces_z.shape[0]:
        Warning("Different numbers of cells + traces! check yourself girl")

    sorted_footies = footies[sorted_ind]
    footies_c = color_footies(sorted_footies)
    plt.imshow(footies_c.max(axis=0))
    plt.show()


def color_footies(footies):
    '''
    footies: 3D array Nxd1xd2 N cells by image size
    colormap: colormap from matplotlib.cm

    '''
    colormap = mpl.cm.get_cmap('Reds_r')
    N = footies.shape[0] # number of footprints in FC session
    colors = np.linspace(0, 1, N)
    cmap = colormap(colors)
    footies_c = np.zeros(footies.shape + (4,))  # Extend to 4 channels for RGBA colors
    for i in range(N):
        footies_c[i] = cmap[i] * footies[i][:, :, np.newaxis]  # Apply color from colormap
    return footies_c
