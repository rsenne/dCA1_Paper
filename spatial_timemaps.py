import sys
from scipy.stats import zscore
sys.path.extend(['/Users/amonast/Documents/GitHub/dCA1_paper'])
import onep.onephoton as onep
from onep.Old_Analyses.cell_registration import CellReg
import matplotlib as mpl
import matplotlib.pyplot as plt
from trace_analysis_functions import eta_individual_cells
import numpy as np
import seaborn as sb

def main():
#ROI MAPS - FC 
#FC traces 
    astro = onep.InscopixProcessing(session='fc', animal='astro3', data_directory='/Users/amonast/Desktop/dCA1_astro')
    session_ind = 0
    collection = onep.dCA1Group(astro)
    fc_traces =collection.grab_all_traces().to_numpy().T
    cellreg = CellReg(astro.animal,'FOV1',N_sessions=1,session_inds=[session_ind])

    foots=astro.load_footprints(session_subset=[0])
    footies = foots[session_ind][astro.accepted_inds]
    plt.imshow(footies.max(axis=0))
    plt.show()

    timestamps = astro.Timestamps[0:3303]
    fc_ctxa_traces_z = zscore(fc_traces[:,0:3303], axis=1)

    ax,across_eta,time=eta_individual_cells(data=fc_ctxa_traces_z, timestamps=timestamps[:3303], events=[[120,180,240,300], ], window=28)
    max_indices = np.argmax(across_eta, axis=1)

    time = np.linspace(-14, 28, 5)
    sorted_ind = np.argsort(max_indices)
    sorted_arr = across_eta[sorted_ind]
    fig, ax = plt.subplots()
    ax.axvline(x=105, color='white', linestyle='--')
    sb.heatmap(sorted_arr, cmap='mako',cbar=True, cbar_kws={"label": r"z-scored $\frac{dF}{F}$"})
    ax.set_xticks(np.linspace(0, len(across_eta.T), 5), time)
    ax.set_title('FC: Astro dCA1 Shock #1')
    ax.set_xlabel('Time (seconds)')
    plt.show()

    if footies.shape[0]!=fc_ctxa_traces_z.shape[0]:
        Warning("Different numbers of cells + traces! check yourself girl")
    
    N= footies.shape[0]
    colormap=mpl.cm.get_cmap('jet')
    colors = np.linspace(0,1,N)
    ncolors = [colormap(colors[i]) for i in range(len(colors))]

    sorted_footies = footies[sorted_ind]
    color_ints = np.arange(1,N+1)
    footies_c = color_footies(sorted_footies,'jet')
    plt.imshow(footies_c.max(axis=0),cmap='jet')


def color_footies(footies,colormap):
    '''
    footies: 3D array Nxd1xD2 N cells by image size 
    colormap: colormap name string from matplotlib

    '''
    N= footies.shape[0]
    colormap=mpl.cm.get_cmap('jet')
    colors = np.linspace(0,1,N)
    ncolors = [colormap(colors[i]) for i in range(len(colors))]

    color_ints = np.arange(1,N+1)
    footies_c = np.zeros(footies.shape)
    for ii,cell in enumerate(footies):
        color_i = color_ints[ii]
        footies_c[ii,:,:]=cell*colors[ii]
    return footies_c


if __name__=='__main__':
    main()
