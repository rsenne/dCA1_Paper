import os
import numpy as np
import pandas as pd
from tkinter import filedialog,simpledialog
class CellReg:
    def __init__(self):
        self.base_directory = filedialog.askdirectory(title='Choose Experiment Directory')
        self.metadata_file = filedialog.askopenfilename(title='Choose metadata csv file')
        self.animal = simpledialog.askstring(prompt='Enter animal name')
        self.FOV = simpledialog.askstring(prompt='Enter FOV')

    def convert_foots_to_masks(footprints):
        '''
        converts footprints to binary masks of 0s and 1s
        footprints: n x Y x X array of cell masks, background must be 0 , cell rois must be >0
        returns footprints with cell rois set to 1
        '''
        footprints[footprints > 0] = 1
        return footprints

    def get_reg_ind(self):
        '''
        get registered indices from CellReg and summary images from all sessions
        :param animal: animal name, str
        :param FOV: fov name,str
        :param file_key: metadata csv for experiment
                        #Note: Session names should be alphabetized in temporal order i.e. session1,session2 or,
                         baseline1,baseline2,post1,post2. This ensures getting data for multiple sessions are in the right order.
        :param base_path: base directory for processed data
        :return: reg_ind: array, python equivalent of cell_to_index_map from CellReg output data.
                        N x M: N unique cells for all sessions, M sessions

        '''
        info = pd.read_csv(self.metadata_file)
        # First get cell registration indices from CellReg output file & convert to pythonic indexing
        # each column is a session, each row is a cell. each entry is that cell's index in that session. if cell was absent its entry is -1
        reg_path = os.path.join(self.base_directory, 'CellReg' + os.path.sep + self.animal + '_' + self.FOV + os.path.sep)
        reg_file = [os.path.join(reg_path, f) for f in os.listdir(reg_path) if 'cellRegistered' in f]
        file = h5py.File(reg_file[-1], 'r') # chooses the last cellreg output file in the directory, make sure theres only 1 present!
        group = file.get('cell_registered_struct')
        dset = group.get('cell_to_index_map')
        reg_ind = dset[()] - 1  # converting to python indexing
        reg_ind = reg_ind.T
        reg_ind = reg_ind.astype('int')
        print(str(reg_ind.shape[0]) + ' Unique cells detected in registration')  # how many cells in total detected

        return reg_ind

    def plot_overlay_footprints(session_inds, reg_foots, cmap='jet', scale_factor=1):
        '''
        session_inds: list or array of which indices of which sessions to plot (i.e. 0 = session 1)
        reg_foots: registered footprints from all sessions, list or array, len N with with YxX arrays or N x Y x X array of N sessions (2D for each session-multiple cells)
        cmap: colomap string
        scale_factor: for plotting scaling
        return: overlay image of aligned footprints
        '''
        if type(reg_foots) == list:
            array_foots = np.array(reg_foots)
            overlay_foots = array_foots.sum(axis=0)
        else:
            overlay_foots = reg_foots.sum(axis=0)
        dims = (overlay_foots.shape[0], overlay_foots.shape[1])

        return hv.Image(overlay_foots).opts(cmap=cmap, colorbar=True, width=dims[1] * scale_factor,
                                            height=dims[0] * scale_factor, clabel='session index')

    # image color limits function, use for single plot instances
    def im_scale(I, min_pct='default', max_pct='default'):
        '''
        Sets colorbar limits
        :param I: array, Image to be plotted
        :param min_pct: default = minimum pixel value of image is lower limit,
                        float/int: percentile of pixel values to plot as minimum value in image
        :param max_pct: min_pct: default = maximum pixel value of image is lower limit,
                        float/int: percentile of pixel values to plot as maximum value in image
        :return: (vmin,vmax), tuple of min and max pixel values to set as color limits.
        '''
        if min_pct == 'default':
            vmin = np.amin(np.unique(I[I > 0]))  # first positive value as min for colormap
        elif min_pct == 'min':
            vmin = np.min(I)
        elif (type(min_pct) == float) or (type(min_pct) == int):
            vmin = np.percentile(I, min_pct)
        if max_pct == 'default':
            vmax = np.max(I)
        elif (type(max_pct) == float) or (type(max_pct) == int):
            vmax = np.percentile(I, max_pct)
        return (vmin, vmax)

    def roi_plot(footprints, idx, image, min_pct='default', max_pct='default', scale_factor: int = 2, cmap_roi='hsv',
                 cmap_image='gray'):
        '''
        plot one cell's roi over a bacgkround image as a patch
        :param cnm: cnmf object
        :param idx: cell index to plot, if -1 no cell is plotted
        :param image: background image to plot over
        :param min_pct: minimum percentile of background image to set as colorbar minimum
        :param max_pct: maximum percentile of background image to set as colorbar maximum
        :param scale_factor: scale dimensions of images
        :param: cmap_roi: colormap for roi
        :param cmap_image: image color map
        :return:
        '''
        dims = image.shape if image is not None else (footprint.shape[1], footprint.shape[2])
        roi = footprints[idx, :, :].copy()
        roi[roi == 0] = np.nan
        clim = im_scale(image, min_pct, max_pct)
        if image is not None:
            if idx != -1:
                plot = hv.Image(image).opts(cmap=cmap_image, clim=clim, width=int(dims[1] * scale_factor),
                                            height=int(dims[0] * scale_factor)) * hv.Image(roi).opts(cmap=cmap_roi,
                                                                                                     alpha=.5)
            elif idx == -1:
                plot = hv.Image(image).opts(cmap=cmap_image, clim=clim, width=int(dims[1] * scale_factor),
                                            height=int(dims[0] * scale_factor)) * hv.Image(roi).opts(cmap=cmap_roi,
                                                                                                     alpha=0)
        else:
            plot = hv.Image(roi).opts(cmap=cmap_roi, width=int(dims[1] * scale_factor),
                                      height=int(dims[0] * scale_factor), alpha=.5)
        return plot

    def rois_plot(footprint, image, idxs=None, min_pct='default', max_pct='default', scale_factor: int = 2,
                  cmap_roi='hsv', cmap_image='gray'):
        '''plot multiple cells rois over a bacgkround image as patches
        :param footprint: footprint of all cells, cells x Xdim x Ydim
        :param idx: cell index to plot, if -1 no cell is plotted
        :param image: background image to plot over
        :param min_pct: minimum percentile of background image to set as colorbar minimum
        :param max_pct: maximum percentile of background image to set as colorbar maximum
        :param scale_factor: scale dimensions of images
        :param: cmap_roi: colormap for roi
        :param cmap_image: image color map
        :return:
        '''
        dims = image.shape if image is not None else (footprint.shape[1], footprint.shape[2])
        if idxs is None:  # allows you to plot only some cells
            idxs = np.arange(0, footprint.shape[0])
        sum_masks = np.sum(footprint[idxs, :, :], axis=0)
        sum_masks[sum_masks == 0] = np.nan
        if image is not None:
            clim = im_scale(image, min_pct, max_pct)

            plot = hv.Image(image).opts(cmap=cmap_image, clim=clim, width=int(dims[1] * scale_factor),
                                        height=int(dims[0] * scale_factor)) * hv.Image(sum_masks).opts(cmap='hsv',
                                                                                                       alpha=.5)
        else:
            plot = hv.Image(sum_masks).opts(cmap=cmap_roi, width=int(dims[1] * scale_factor),
                                            height=int(dims[0] * scale_factor), alpha=.5)
        return plot

    def discrete_colorscale(bvals, colors):
        """
        bvals - list of values bounding intervals/ranges of interest
        colors - list of rgb or hex colorcodes for values in [bvals[k], bvals[k+1]],0<=k < len(bvals)-1
        returns the plotly  discrete colorscale
        """
        if len(bvals) != len(colors) + 1:
            raise ValueError('len(boundary values) should be equal to  len(colors)+1')
        bvals = sorted(bvals)
        bvals = np.array(bvals)
        nvals = [(v - bvals[0]) / (bvals[-1] - bvals[0]) for v in bvals]  # normalized values

        dcolorscale = []  # discrete colorscale
        for k in range(len(colors)):
            dcolorscale.extend([[nvals[k], colors[k]], [nvals[k + 1], colors[k]]])
        return dcolorscale

    def plot_A_discrete_multisession(n, footprint, images_list, footprint_threshold, indices_lists, ticktexts,
                                     colors_list, opacity=0.5, max_pct=None):  # updated from Y Zaki
        '''
        n: int, number of sessions to ploy
        A : 3d array
            array of spatial footprints, first dimension should be cells
        images_list: list of 2d image arrays
            list of image arrays for plotting
        indices_lists : list of list of arrays
            a list of the lists of cell indices to plot on each subplot
            each list item is a set of cell indices, where each set of cell indices will be colored one discrete color
        ticktexts : list of list of strings
            list of labels for each plot
            each string will correspond to a label defining that set of indices
        colors : list of strings of RGB hex values
            each color will correspondn to the color of that set of cells
        opacity : float
            the opacity of the footprints overlaid onto max projection. default is 0.4
        '''

        fig = make_subplots(rows=1, cols=n, horizontal_spacing=0.05, shared_yaxes=True, shared_xaxes=True)
        cx = 0
        for j in np.arange(0, n):
            A = footprint[j]
            max_proj = images_list[j]
            indices_list = indices_lists[j]
            ticktext = ticktexts[j]
            colors = colors_list[j]
            sub_stacks = []
            i = 0.5
            cx = + j
            tickvals = []

            for indices in indices_list:
                sub_maxA = A[indices, :, :].max(axis=0)
                sub_maxA[sub_maxA > footprint_threshold] = i
                tickvals.append(i)
                i += 1
                sub_stacks.append(sub_maxA)

            bvals = np.arange(0, len(indices_list) + 1)
            dcolorsc = discrete_colorscale(bvals, colors)

            final_maxA = np.dstack(sub_stacks)
            final_maxA = final_maxA.max(axis=2)
            final_maxA[final_maxA <= footprint_threshold] = np.nan

            zmin = im_scale(max_proj)[0]
            if max_pct is None:
                zmax = im_scale(max_proj, max_pct=95)[1]
            else:
                zmax = im_scale(max_proj, max_pct=max_pct)[1]

            fig.add_trace(go.Heatmap(z=max_proj, colorscale='gray', showscale=False, zmin=zmin, zmax=zmax), 1, j + 1)
            fig.add_trace(go.Heatmap(z=final_maxA, colorscale=dcolorsc, opacity=opacity, showscale=False, zmin=0,
                                     zmax=len(indices_list),
                                     colorbar=dict(thickness=15, tickvals=tickvals, ticktext=ticktext, x=cx)), 1, j + 1)
            fig.update_xaxes({'visible': False, 'showticklabels': False})
            fig.update_yaxes({'visible': False, 'showticklabels': False})
            fig.update_layout(yaxis=dict(autorange='reversed'), template='simple_white', width=500 * n, height=500,
                              font=dict(size=13), dragmode='pan', margin=dict(l=40, r=40, t=60, b=40))
            fig.update_xaxes(matches='x')
        return fig
