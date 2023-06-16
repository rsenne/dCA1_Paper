import os
import numpy as np
import pandas as pd
from tkinter import filedialog,simpledialog
import h5py
import caiman as cm
import tifffile
__all__=['CellReg']
class CellReg:
    def __init__(self):
        self.base_directory = filedialog.askdirectory(title='Choose Experiment Directory')
        self.metadata_file = filedialog.askopenfilename(title='Choose metadata csv file')
        self.animal = simpledialog.askstring(title='Experiment info',prompt='Enter animal name')
        self.FOV = simpledialog.askstring(title='Experiment info',prompt='Enter FOV name')

        self.metadata = pd.read_csv(self.metadata_file)
    def load_footprints_3D(self,select_sessions=False):
        '''
        :param select_sessions: default False. if True user clicks the footprint .mat files indivudally in chronological order.
        :return:
            self.footprints: list of N sessions, each entry is a 3D array of binarized cell roi footprints from that session
        '''
        if select_sessions:
            self.footprint_files = filedialog.askopenfilenames(title="Select the footprint files in chronological order of sessions")
            for i in range(N):
                foot_file= filedialog.askopenfilename() ##CLICK THE FILES IN CHRONO ORDER!
                self.footprint_files.append(footfile)
        else:
            sessions = self.metadata['Session'].loc[(self.metadata['Animal']==self.animal)&(self.metadata['FOV']==self.FOV)].values()
            print('Make sure these are in order: ')
            print(sessions)
            print('If theyre not in order, run load_og_footprints again and set select sessions to True to put them in order')

            footprint_path =os.path.join(self.base_directory,'CellReg',self.animal+'_'+self.FOV,'converted_maps')
            footprint_files = [os.path.join(footprint_path,file) for file in os.listdir(footprint_path) if '.mat' in file]

        foots_float =[]
        for f in footprint_files:
            foot_file = h5py.File(f, 'r')
            foot_file.get('this_session_converted_footprints')[()].transpose((2, 1, 0))
            foots_float.append(foot_file.get('this_session_converted_footprints')[()].transpose((2, 1, 0)))

        self.footprints = [self.convert_foots_to_masks(foots_float[i]) for i in range(len(foots_float))]  # must convert to masks if imported footprints from inscopix helper files.        return self.footprints
        return self.footprints
    def load_shifted_footprints_2D(self):
        '''
        Load in multiple 3D arrays of shifted footprints from each session.
        Footprints are shifted relative to inscopix images but aligned from CellReg ouptut
        :return:
            self.footprints_reg: list of N sessions,
                                each entry is a 3D array of binarized cell roi footprints from that session, with applied shifts from CellReg
        '''
        aligned_map_file = h5py.File(os.path.join(self.base_directory,'CellReg',self.animal + '_' + self.FOV, 'aligned_data_struct.mat'))
        aligned_struct = aligned_map_file['aligned_data_struct']
        self.footprints_reg = []
        for i in range(N):
            foot_aligned = aligned_map_file[aligned_struct['footprints_projections_corrected'][i, 0]][()].transpose((1, 0))
            sum_foot_aligned = self.convert_foots_to_masks(foot_aligned)
            self.footprints_reg.append(sum_foot_aligned)
        return self.footprints_reg
    def convert_foots_to_masks(footprints):
        '''
        converts footprints to binary masks of 0s and 1s
        footprints: n x Y x X array of cell masks, background pixels must be 0, pixels corresponding to cell rois must be > 0
        returns footprints with pixels within cell rois set to 1
        '''
        footprints[footprints > 0] = 1
        return footprints

    def get_reg_ind(self):
        '''
        Get table of registered indices from CellReg from all sessions
        :param animal: animal name, str
        :param FOV: fov name,str
        :param file_key: metadata csv for experiment
                        #Note: Session names should be alphabetized in temporal order i.e. session1,session2 or,
                         baseline1,baseline2,post1,post2. This ensures getting data for multiple sessions are in the right order.
        :param base_path: base directory for processed data
        :return: reg_ind: array, N x M: N unique cells for all sessions, M sessions
                                python equivalent of cell_to_index_map from CellReg output data.
                                Lookup table of registered cells from each session.

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
    def generate_corr_images(self,save=True):
        '''
        Generate correlation image; reliant on Caiman packages
        :return: corr_ims: list of 2d correlation image arrays
        '''
        mc_movie_path = os.path.join(self.base_directory,'Summary Images','MC')
        mc_movie_files = [os.pathljoin(mc_movie_path) for file in os.listdir(mc_movie_path) if 'MC_Movie.tif' in file]

        self.corr_ims = []
        for file in mc_movie_files:
            movie = cm.load(file)
            Cn = cm.local_correlations(movie.transpose(1, 2, 0))
            self.corr_ims.append(Cn)
            if save:
                tifffile.imwrite(os.path.join(mc_movie_path,self.animal+'_'+self.animal+'_CorrImage.tif'))

        return self.corr_ims

    def get_summary_images(self,image_type='max dff'):
        if image_type not in ['max dff', 'mean', 'min', 'max', 'std','corr']:
            raise Exception("Image type not supported, choose max dff, mean, min, max, std or corr")
        if image_type=='max dff':
            images_path = os.path.join(self.base_directory,'Summary_images',self.animal+'_'+self.FOV,'DFF')
        else:
            images_path = os.path.join(self.base_directory,'Summary_images',self.animal+'_'+self.FOV,'MC')

###### plotting functions #########
    def plot_overlay_footprints(self.footprints_reg,session_inds=None, cmap='jet', scale_factor=1):
        '''
        Notebook plotting function to overlay the registered sets of ROIs
        session_inds: list or array of which indices of which sessions to plot (i.e. 0 = session 1)
        reg_foots: registered footprints from all sessions, list or array, len N with with YxX arrays or N x Y x X array of N sessions (2D for each session-multiple cells)
        cmap: colormap string
        scale_factor: int, for plotting scaling
        return: holoviews image object of overlay image of aligned footprints
        '''
        #convert list of footprints to 3d array
        if type(self.footprints_reg) == list:
            array_foots = np.array(self.footprints_reg)
        else:
            array_foots=self.footprints_reg
        ### optional, choose only some sessions to overlay
        if session_inds is None:
            overlay_foots = array_foots.sum(axis=0)
        else:
            overlay_foots = array_foots[session_inds,:,:].sum(axis=0)

        dims = (overlay_foots.shape[0], overlay_foots.shape[1])

        return hv.Image(overlay_foots).opts(cmap=cmap, colorbar=True, width=dims[1] * scale_factor,
                                            height=dims[0] * scale_factor, clabel='session index')

    # image color limits function, use for single plot instances
    def im_scale(I, min_pct='default', max_pct='default'):
        '''
        Sets image colorbar limits
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
        plot one cell's roi over a background image as a translucent patch
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
