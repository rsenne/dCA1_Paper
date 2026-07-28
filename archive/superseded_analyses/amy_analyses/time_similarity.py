#%%
import pandas as pd
import numpy as np
import seaborn as sb
import os
from onep.onephoton import *
from scipy.integrate import simpson
import scipy.stats as stats

# set data paths
data_directory = '/Users/amonast/Desktop/dCA1_astro'
animal = 'astro5'
session = 'fc'
# create isx processing object
isx = InscopixProcessing(animal,session,data_directory)
reg_inds = isx.load_registration_table(session_subset=[0,1])

traces = isx.get_traces()
#%%
bin_size_s = 1
frame_rate_ds = 10
frames_p_bin = bin_size_s * frame_rate_ds

traces_b = bin_traces(traces,bin_size = frames_p_bin)
#%% correlation for all time 
C_all = correlation(traces_b)
C_all.get_corr_matrix()
C_all.plot_corr_matrix(vmin=-1,vmax=1)
#%%
## binned correlation matrices
mats = []
times = [(tt,tt+frames_p_bin) for tt in np.arange(0, traces.shape[1], frames_p_bin)]
for t in times:
    act = traces[:,t[0]:t[1]]
    c_act = correlation(act)
    corr_mat_t = c_act.get_corr_matrix()
    mats.append(corr_mat_t)

#%%

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

#%%
fig,ax=plt.subplots()
ims=[]
for i in range(len(mats)):
    im = ax.imshow(mats[i], animated=True,vmin=-1,vmax=1,cmap='seismic')
    ims.append([im])
anim = animation.ArtistAnimation(fig, ims, interval=50, blit=True,
                                repeat_delay=1000)
anim.save('movie.mp4')
#%%
plt.imshow(stats.zscore(traces,axis=1),aspect='auto')
plt.colorbar()
#%%
results = []
for c in range(1,len(mats)):
    c_ij = mats[c-1]
    cprime_ij = mats[c]
    # Compute the sum of products over all pairs using matrix multiplication
    sum_product = np.trace(np.dot(c_ij, cprime_ij.T))

    # Assuming n is the shape of the square matrix
    n = c_ij.shape[0]

    # Compute the final value
    result = 1 / (n * (n - 1)) * sum_product
    results.append(result)

#%%%
def bin_traces(D, bin_size=4,type='integrate'):
    T = D.shape[1]
    t = np.arange(0, T, bin_size)

    n_bins0 = T // bin_size
    if T % bin_size !=0:
        n_bins = n_bins0+1
    elif T % bin_size ==0:
        n_bins = n_bins0
    d_bin = np.empty([D.shape[0],n_bins])
    
    for n in np.arange(0,D.shape[0]):
        d=D[n,:]
        for i in np.arange(0, t.shape[0]):
            if type=='sum':
                d_bin[n,i] = np.sum(d[t[i]:t[i] + bin_size])
            if type=='integrate':
                d_bin[n,i] = simpson(d[t[i]:t[i] + bin_size])
    return d_bin
#%%

class correlation:
    '''
    class for making pairwise correlation matrices
    dff: N x T dF/F traces for N neurons, T frames
    '''
    def __init__(self, dff, idx=None):
        if idx is None:
            self.dff = dff
        else:
            self.dff = dff[idx, :]

    def get_corr_matrix(self,method='spearman'):
        '''
        method: str correlation method. 'spearman' returns spearman rho, or 'kendall' returns kendall tau b
        only works for correlating one set of cell with itself. To correlate one group of cells traces with another use corr_matrix below
        :return: corr_r: NxN correlation matrix. each entry is correlation coefficient r for each pair of cells.
        '''
        corr_r = np.empty([self.dff.shape[0], self.dff.shape[0]])
        if method=='spearman':
            print('using spearman rho')
        elif method=='kendall':
            print('using kendall tau')

        for i in np.arange(0, self.dff.shape[0]):
            dff_1 = self.dff[i]
            for j in np.arange(0, self.dff.shape[0]):
                dff_2 = self.dff[j]
                if method=='spearman':
                    corr_r[i, j] = stats.spearmanr(dff_1, dff_2)[0]
                elif method=='kendall':
                    corr_r[i,j] = stats.kendalltau(dff_1,dff_2)[0]
        self.corr = corr_r
        return corr_r

    def get_lower(self):
        '''
        return: corr_lower: array, non-duplicate values of correlation matrix
        '''
        # get the bottom triangle of the matrix to avoid duplicates
        indu = np.triu_indices(self.corr.shape[0])
        corr_mat = self.corr
        self.corr_lower = corr_mat
        self.corr_lower[indu] = 1
        self.corr_lower = self.corr_lower[self.corr_lower != 1]
        return self.corr_lower

    def plot_corr_matrix(self, vmin, vmax, title: str = None, cmap="seismic",mask_upper=False):
        '''

        :param vmin: minimum r value for colorbar
        :param vmax: maximum r value for colorbar
        :param title: plot title, str
        :param cmap: colormap
        :return:
        '''
        mask = np.triu(np.ones_like(self.corr, dtype=bool)) if mask_upper else None
        f, ax = plt.subplots()
        sb.heatmap(self.corr, mask=mask, cmap=cmap, vmin=vmin, vmax=vmax, center=0, square=True, cbar_kws={"shrink": .5})
        if title is not None:
            plt.title(title)
        plot = plt.show()
        return plot

    def get_clim(self):
        '''
        :return: (vmin,vmax), tuple, min and max r values for setting color scale
        '''
        self.vmin = self.corr.min()
        lower = self.get_lower()
        self.vmax = lower.max()
        return (self.vmin, self.vmax)
# %%
