#%%
import pandas as pd
import numpy as np
import seaborn as sb
import os
from onephoton.onephoton import *
# set data paths
traces_dir = '/Users/amonast/Desktop/dCA1_astro/Cell_Traces'
animal = 'astro5'
session_str = 'fc'
fname = os.path.join(traces_dir,animal+'_traces',animal+'_'+session_str+'_traces.csv')
# create isx processing object
isx = InscopixProcessing(fname,animal,data_directory=os.path.split(traces_dir)[0])
reg_inds = isx.get_registered_cells(session_subset=[0,1])

traces = isx.get_traces()
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

    def plot_corr_matrix(self, vmin, vmax, title: str = None, cmap="seismic"):
        '''

        :param vmin: minimum r value for colorbar
        :param vmax: maximum r value for colorbar
        :param title: plot title, str
        :param cmap: colormap
        :return:
        '''
        mask = np.triu(np.ones_like(self.corr, dtype=bool))
        f, ax = plt.subplots()
        sb.heatmap(self.corr, mask=mask, cmap=cmap, vmin=-0.4, vmax=0.4, center=0, square=True, cbar_kws={"shrink": .5})
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