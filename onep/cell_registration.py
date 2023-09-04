import os
import numpy as np
import pandas as pd
from tkinter import filedialog,simpledialog
import h5py
# import caiman as cm
import tifffile
import holoviews as hv
from plotly.subplots import make_subplots
from pygments.lexers import go
from skimage.transform import warp, AffineTransform
from scipy.io import savemat,loadmat
import warnings

__all__ = ["CellReg"]

class CellReg:
    def __init__(self,animal:str,fov:str='FOV1',N_sessions:int=5,session_inds:int=None):
        '''
        animal: string, animal id (ex 'astro3')
        fov: string 'FOV1'
        N_sessions: int, number of sessions
        session_inds: list: indices of which sessions to pull, use if selecting a subset of sessions. 
                            N_Sessions must be len(session_inds)
        '''
        # self.base_directory = filedialog.askdirectory(title='Choose Experiment Directory')
        # self.metadata_file = filedialog.askopenfilename(title='Choose metadata csv file')
        # self.base_directory = r"C:\Users\RamirezLab\Desktop\Rebecca"
        # self.metadata_file = r"C:\Users\RamirezLab\Desktop\Rebecca\Data_info_astro.csv"
        self.base_directory = "/Users/amonast/Desktop/dCA1_astro"
        self.metadata_file = "/Users/amonast/Desktop/dCA1_astro/Data_info_astro.csv"
        self.animal = animal
        self.FOV = fov
        self.N_sessions = N_sessions
        self.metadata = pd.read_csv(self.metadata_file)
        self.group = self.metadata['Group'].loc[self.metadata['Animal']==self.animal].values[0]
        self.session_inds = session_inds

        if self.group=='EXT':
            self.sessions = ['fc','recall','ext1','ext2','ext3']
        elif self.group=='GEN':
            self.sessions = ['fc','gen1','gen2','gen3','gen4']
        
        if session_inds is not None:
            if not self.N_sessions == len(session_inds):
                raise AttributeError("self.N_sessions not equal to number of subsetted sessions")
            self.sessions = [self.sessions[ind] for ind in session_inds]
            self.session_inds=session_inds
            
            print('only sessions: ')
            print(self.sessions)

######### footprint functions  ###########
    def load_registration_table(self):
        '''
        Loads in final output cell_to_index table after final manual evaluation.
        '''
        path = os.path.join(self.base_directory,'CellReg',self.animal+'_'+self.FOV,self.animal+'_cell_reg.csv')
        
        df = pd.read_csv(path,header=None)
        df.fillna(-1000,inplace=True) # fill those cells that weren't checked for other days with index -1000

        if self.session_inds is not None:
            print('Loading in registration table for only: ')
            print(self.sessions)
            try:
                self.registration_table = df.iloc[:,self.session_inds].astype(int)
            except IndexError:
                print('N sessions exceeds sessions in CellReg output csv. Loading in original CellReg output table.')
                self.registration_table = df.iloc[:,0:self.N_sessions].astype(int)
        else:
            self.registration_table = df.iloc[:,0:self.N_sessions].astype(int)

        if self.registration_table.shape[1]!=self.N_sessions:
            print("Warning: only "+str(self.registration_table.shape[1])+ " sessions found in CellReg output csv: ")
            print(path)

        #drop rows where all cells are -1000 unchecked - for grabbing certain sessions only
        self.registration_table=self.registration_table.iloc[~(self.registration_table==-1000).all(axis='columns').values]

        return self.registration_table

    def load_footprints_3D(self,select_sessions=False,affine_shifted=False):
        '''
        :param select_sessions: default False. if True user clicks the footprint .mat files indivudally in chronological order.
        :param affine_shifted: use original footprints or affine shifted ones 
        :return:
            self.footprints: list of N sessions, each entry is a 3D array of binarized cell roi footprints from that session
        '''
        if select_sessions:
            self.footprint_files = filedialog.askopenfilenames(title="Select the footprint files in chronological order of sessions")
            for i in range(self.N_sessions):
                foot_file= filedialog.askopenfilename() ##CLICK THE FILES IN CHRONO ORDER!
                self.footprint_files.append(foot_file)
        else:
            sessions = self.metadata['Session'].loc[(self.metadata['Animal']==self.animal)&(self.metadata['FOV']==self.FOV)].values
            print('Make sure these are in order: ')
            print(sessions)
            print('If theyre not in order, run load_footprints_3D again and set select sessions to True to put them in order')

        if affine_shifted:
            footprint_path = os.path.join(self.base_directory,'CellReg',self.animal+'_'+self.FOV,'shifted_footprints')
            footprint_files = [os.path.join(footprint_path,self.animal+'_'+self.FOV+'_'+session+'_shifted_footprints.mat') for session in self.sessions]
            print(footprint_files)
            foots_float =[]
            for f in footprint_files:
                try:
                    foot_file = h5py.File(f, 'r')
                except:
                    foot_file = loadmat(f)
                foots_float.append(foot_file.get('footprints_shifted')[()])
        else:
            footprint_path =os.path.join(self.base_directory,'CellReg',self.animal+'_'+self.FOV,'converted_maps')
            footprint_files = [os.path.join(footprint_path,self.animal+'_'+session+'_G&B_converted.mat') for session in self.sessions]
            print(footprint_files)

            foots_float =[]
            for f in footprint_files:
                foot_file = h5py.File(f, 'r')
                foots_float.append(foot_file.get('this_session_converted_footprints')[()].transpose((2, 1, 0)))

        self.footprints = [self.convert_foots_to_masks(foots_float[i]) for i in range(len(foots_float))]  # must convert to masks if imported footprints from inscopix helper files. 
        
        try:
            if self.session_inds is not None:
                self.footprints=[self.footprints[i] for i in self.session_inds]
        except AttributeError:
            pass

        return self.footprints
   
    def load_shifted_footprints_2D(self):
        '''
        Load in multiple 2D array of all shifted footprints from CellReg.
        Footprints are shifted relative to inscopix images but aligned from CellReg ouptut
        ** this includes all the cells given to CellReg including Isx rejected cells ** 
        to exclude rejected cells use load_footprints_3D and 
            self.footprints_reg: list of N sessions,
                                each item is a 3D array of binarized cell roi footprints from that session, with applied shifts from CellReg
        '''
        aligned_map_file = h5py.File(os.path.join(self.base_directory,'CellReg',self.animal + '_' + self.FOV, 'aligned_data_struct.mat'))
        aligned_struct = aligned_map_file['aligned_data_struct']
        self.footprints_reg = []
        for i in range(self.N_sessions):
            foot_aligned = aligned_map_file[aligned_struct['footprints_projections_corrected'][i, 0]][()].transpose((1, 0))
            sum_foot_aligned = self.convert_foots_to_masks(foot_aligned)
            self.footprints_reg.append(sum_foot_aligned)
        return self.footprints_reg

    def resize_foots(self,select_sessions=False):
        footprints = self.load_footprints_3D(select_sessions=select_sessions,)
        cells = [im.shape[0] for im in footprints]
        rows = [im.shape[1] for im in footprints]
        cols = [im.shape[2] for im in footprints]
        i = np.min(rows)
        j = np.min(cols)
        resized = [footprint[:,0:i,0:j] for footprint in footprints]
        
        return resized

    def convert_foots_to_masks(self,footprints):
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
        self.reg_ind = reg_ind.astype('int')
        print(str(reg_ind.shape[0]) + ' Unique cells detected in registration')  # how many cells in total detected

        return self.reg_ind

######### image functions ##########
    def resize_images(self,image_type,shifted = True,session_inds=None):
        image_files = self.get_summary_images(image_type,shifted=shifted,session_inds=session_inds)
        images = [tifffile.imread(file) for file in image_files]
        rows = [im.shape[0] for im in images]
        cols = [im.shape[1] for im in images]
        i = np.min(rows)
        j = np.min(cols)
        resized = [im[0:i,0:j] for im in images]
        return resized
    
    def generate_corr_images(self,save=True):
        '''
        Generate correlation image; reliant on Caiman packages
        :return: corr_ims: list of 2d correlation image arrays
        '''
        mc_movie_path = os.path.join(self.base_directory,'Summary_Images','MC')
        mc_movie_files = [os.path.join(mc_movie_path) for file in os.listdir(mc_movie_path) if 'MC_Movie.tif' in file]

        self.corr_ims = []
        for file in mc_movie_files:
            movie = cm.load(file)
            Cn = cm.local_correlations(movie.transpose(1, 2, 0))
            self.corr_ims.append(Cn)
            if save:
                tifffile.imwrite(os.path.join(mc_movie_path,self.animal+'_'+self.FOV+'_CorrImage.tif'))

        return self.corr_ims
    
    def get_summary_images(self,image_type='max dff',shifted=True,session_inds=None):
        if image_type not in ['max dff', 'mean', 'min', 'max', 'std','corr']:
            raise Exception("Image type not supported, choose max dff, mean, min, max, std or corr")

        if image_type=='max dff':
            if not shifted:
                images_path = os.path.join(self.base_directory,'Summary_Images',self.animal+'_'+self.FOV,'DFF')
            else:
                images_path = os.path.join(self.base_directory,'Summary_Images',self.animal+'_'+self.FOV,'affine_shifted_images')
        else:
            if not shifted:
                images_path = os.path.join(self.base_directory,'Summary_Images',self.animal+'_'+self.FOV,'MC')
            if shifted:
                raise Exception('No shifted images of this type exist')
        try:
            if image_type == 'max dff':
                image_files = [os.path.join(images_path,f) for f in os.listdir(images_path)]
            elif image_type == 'max':
                image_files = [os.path.join(images_path,f) for f in os.listdir(images_path) if 'MaxProj' in f]
            elif image_type == 'mean':
                image_files = [os.path.join(images_path,f) for f in os.listdir(images_path) if 'MeanProj' in f]
            elif image_type == 'min':
                image_files = [os.path.join(images_path,f) for f in os.listdir(images_path) if 'MinProj' in f]
            elif image_type == 'std':
                image_files = [os.path.join(images_path,f) for f in os.listdir(images_path) if 'STDProj' in f]
            elif image_type == 'corr':
                image_files = [os.path.join(images_path,f) for f in os.listdir(images_path) if 'CorrImage' in f]
        except FileNotFoundError:
            print('Image files not found please check filepaths & image type')

        image_files.sort()
        
        try:
            if self.group == 'EXT':
                self.image_files = [image_files[3],image_files[-1],image_files[0],image_files[1],image_files[2]]
            elif self.group =='GEN':
                self.image_files = image_files
            
            if session_inds is not None:
                self.image_files = [self.image_files[ind] for ind in session_inds]
        
        except IndexError:
            self.image_files = image_files
        print(image_files)
        return self.image_files

######## affine transform functions ###########
    def export_affine_shift_footprints(self,footprints_all,X_shifts,Y_shifts,Rotations,Shears,session_inds=None):
        try:
            os.mkdir(os.path.join(self.base_directory,'CellReg',self.animal+'_'+self.FOV))
        except FileExistsError:
            print('Path exists '+ os.path.join(self.base_directory,'CellReg',self.animal+'_'+self.FOV))
        try:
            os.mkdir(os.path.join(self.base_directory,'CellReg',self.animal+'_'+self.FOV,'shifted_footprints'))
        except FileExistsError:
            print('Path exists '+ os.path.join(self.base_directory,'CellReg',self.animal+'_'+self.FOV,'shifted_footprints'))

        savepath = os.path.join(self.base_directory,'CellReg',self.animal+'_'+self.FOV,'shifted_footprints')
        
        if session_inds is not None:
            num_sessions = len(session_inds)
        else:
            num_sessions = self.N_sessions
        
        for i in range(num_sessions):
            shift_x = X_shifts[i]
            shift_y = Y_shifts[i]
            rotation = Rotations[i]
            session = self.sessions[i]
            shear = Shears[i]
            footprints = footprints_all[i]

            shifted = self.apply_shifts_to_footprints(footprints,shift_x,shift_y,rotation,shear)
            
            savemat(os.path.join(savepath,self.animal+'_'+self.FOV+'_'+session+'_shifted_footprints.mat'),{'footprints_shifted':shifted,'shift_x':shift_x,'shift_y':shift_y,'rotation':rotation,'shear':shear})

    def export_affine_shift_images(self,images,X_shifts,Y_shifts,Rotations,Shears):
        im_path = os.path.join(self.base_directory,'Summary_Images', self.animal+'_'+self.FOV,'affine_shifted_images')
        
        if not os.path.exists(im_path):
            print(True)
            try:
                os.mkdir(os.path.split(im_path)[0]) 
            except FileExistsError:
                print('Path exists '+ os.path.split(im_path)[0])
            print(True)
            try:
                os.mkdir(im_path)
            except FileExistsError:
                print('Path exists '+ im_path)

        shift_images = []
        for i,im in enumerate(images):
            shift_x = X_shifts[i]
            shift_y = Y_shifts[i]
            rotation =Rotations[i]
            session = self.sessions[i]
            shear = Shears[i]

            if i ==0:
                im_shifted=im.copy()
            else:
                im_shifted = self.apply_shifts_image(im,shift_x,shift_y,rotation,shear)        
            shift_images.append(im_shifted)
        
            tifffile.imwrite(os.path.join(im_path, self.animal + '_' + self.FOV + '_' + session + '_affine_shift.tif'), im_shifted)
    
    def apply_shifts_to_footprints(self,footprints_3D,translation_x=0,translation_y=0,rotation=0,shear=0):
        print(footprints_3D.shape)
        tform = AffineTransform(scale=(1.0, 1.0), rotation=rotation, shear=shear,
                            translation=(translation_x,translation_y))
        shifted_cells = []
        for cell in footprints_3D:
            shift_cell = warp(cell, tform.inverse)
            shifted_cells.append(shift_cell)
            
        return np.array(shifted_cells)
    
    def apply_shifts_image(self,image,translation_x=0,translation_y=0,rotation=0,shear=0):
        tform = AffineTransform(scale=(1.0, 1.0), rotation=rotation, shear=shear,
                                translation=(translation_x,translation_y))
        im_t = warp(image, tform.inverse)
        return im_t    
    
    def plot_overlaid_rgb(self,im1,im2,scale_factor=3,gain=5,alpha=0.8):
            rgb = hv.RGB(np.dstack([im1*gain,im2*gain,np.zeros((im1.shape[0],im1.shape[1]))])).opts(width=int(im1.shape[1])*scale_factor,
                                                                                                height=int(im1.shape[0])*scale_factor,alpha=alpha)
            return rgb
    
    def plot_translate(self,im1,im2,shift_x,shift_y,rotation=0,shear=0,gain=3):
        tform = AffineTransform(scale=(1.0, 1.0), rotation=rotation, shear=shear,
                            translation=(shift_x,shift_y))
        im2_t = warp(im2, tform.inverse)
        return self.plot_overlaid_rgb(im1,im2_t,gain=gain)
    
###### plotting functions #########
    def plot_overlay_footprints(self,session_inds=None, cmap='jet', scale_factor=1):
        '''
        Notebook plotting function to overlay the registered sets of ROIs
        session_inds: list or array of which indices of which sessions to plot (i.e. 0 = session 1)
        reg_foots: registered footprints from all sessions, list or array, len N with with YxX arrays or N x Y x X array of N sessions (2D for each session-multiple cells)
        cmap: colormap string
        scale_factor: int, for plotting scaling
        return: holoviews overlay object
        '''
        #convert list of footprints to 3d array
        try:
            if type(self.footprints_reg) == list:
                array_foots = np.array(self.footprints_reg)
            else:
                array_foots=self.footprints_reg
        except AttributeError:
            self.load_shifted_footprints_2D()
        ### optional, choose only some sessions to overlay
        if session_inds is None:
            overlay_foots = array_foots.sum(axis=0)
        else:
            overlay_foots = array_foots[session_inds,:,:].sum(axis=0)

        dims = (overlay_foots.shape[0], overlay_foots.shape[1])

        return hv.Image(overlay_foots).opts(cmap=cmap, colorbar=True, width=dims[1] * scale_factor,
                                            height=dims[0] * scale_factor, clabel='session index')

    def im_scale(self,I, min_pct='default', max_pct='default'):
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

    def roi_plot(self, session_ind,idx,image=None,min_pct='default', max_pct='default', scale_factor: int = 2, cmap_roi='hsv',
                 cmap_image='gray'):
        ''' (Notebook) Plot one cell's roi over a background image as a translucent patch
        :param session_ind: which session to plot cells
        :param image: background image to plot over, optional, if None will just plot footprint
        :param idx: cell index to plot, *if -1 no cell is plotted*
        :param min_pct: minimum percentile of background image to set as colorbar minimum
        :param max_pct: maximum percentile of background image to set as colorbar maximum
        :param scale_factor: scale dimensions of images
        :param: cmap_roi: colormap for roi
        :param cmap_image: image color map
        :return: Holoviews image overlay object
        '''
        footprints = self.footprints[session_ind]
        dims = image.shape if image is not None else (footprints.shape[1], footprints.shape[2])
        roi = footprints[idx, :, :].copy()
        roi[roi == 0] = np.nan
        clim = self.im_scale(image, min_pct, max_pct)
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

    def rois_plot(self, session_ind,idxs=None,image=None, min_pct='default', max_pct='default', scale_factor: int = 2,
                  cmap_roi='hsv', cmap_image='gray'):
        ''' (Notebook) Plot multiple cells rois over a bacgkround image as patches
        :param session_ind: which session to plot cells
        :param image: background image to plot over, optional, if None will just plot footprint
        :param idxs: cell index to plot, *if -1 no cell is plotted*
        :param min_pct: minimum percentile of background image to set as colorbar minimum
        :param max_pct: maximum percentile of background image to set as colorbar maximum
        :param scale_factor: scale dimensions of images
        :param: cmap_roi: colormap for roi
        :param cmap_image: image color map
        :return: Holoviews image overlay object
        '''
        footprints = self.footprints[session_ind]
        dims = image.shape if image is not None else (footprints.shape[1], footprints.shape[2])
        if idxs is None:  # allows you to plot only some cells
            idxs = np.arange(0, footprints.shape[0])
        sum_masks = np.sum(footprints[idxs, :, :], axis=0)
        sum_masks[sum_masks == 0] = np.nan

        if image is not None:
            clim = self.im_scale(image, min_pct, max_pct)

            plot = hv.Image(image).opts(cmap=cmap_image, clim=clim, width=int(dims[1] * scale_factor),
                                        height=int(dims[0] * scale_factor),xaxis=None,yaxis=None) * hv.Image(sum_masks).opts(cmap='hsv',
                                                                                                       alpha=.5)
        else:
            plot = hv.Image(sum_masks).opts(cmap=cmap_roi, width=int(dims[1] * scale_factor),
                                            height=int(dims[0] * scale_factor), alpha=.5,xaxis=None,yaxis=None)
        return plot

    def plot_im_stack(self,images,titles=None,cmap='gray',scale_factor=3):
        if titles ==None:
            im_dict = {i: hv.Image(im).opts(width=int(im.shape[1])*scale_factor,height=int(im.shape[0])*scale_factor,cmap=cmap,xaxis=None,yaxis=None) for i,im in enumerate(images)}
        else:
            im_dict = {titles[i]: hv.Image(im).opts(width=int(im.shape[1])*scale_factor,height=int(im.shape[0])*scale_factor,cmap=cmap,xaxis=None,yaxis=None) for i,im in enumerate(images)}
        hmap = hv.HoloMap(im_dict,kdims=['images'])
        return hmap
    
    def discrete_colorscale(self,bvals, colors):
        """
        Creates plotly discrete colorscale for
        bvals: list of values bounding intervals/ranges of interest
        colors: list of rgb or hex colorcodes for values in [bvals[k], bvals[k+1]],0<=k < len(bvals)-1
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

    def plot_A_discrete_multisession(self,n,session_inds, images_list, footprint_threshold, indices_lists, ticktexts,
                                     colors_list, opacity=0.5, max_pct=0.95):  # updated from Y Zaki
        '''
        n: int, number of sessions to plot
        footprint : 3d array
            array of spatial footprints, cells x Y x X
        images_list: list of 2d image arrays
            list of image arrays for plotting
        footprint threshold: value for threshold on rois, i.e. if all rois footprints are > 0, this is 0
        indices_lists : list of list of arrays
            a list of the groups of cell indices to plot on each subplot
            each list item is a set of cell indices, where each set of cell indices will be colored one discrete color
        ticktexts : list of list of strings
            list of labels for each plot
            each string will correspond to a label defining that set of indices
        colors : list of strings of RGB hex values
            each color will correspond to the color of that set of cells
        opacity : float
            the opacity of the footprints overlaid onto max projection. default is 0.4
        '''

        fig = make_subplots(rows=1, cols=n, horizontal_spacing=0.05, shared_yaxes=True, shared_xaxes=True)
        cx = 0
        
        for j in session_inds:
            A = self.footprints[j]
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
            dcolorsc = self.discrete_colorscale(bvals, colors)

            final_maxA = np.dstack(sub_stacks)
            final_maxA = final_maxA.max(axis=2)
            final_maxA[final_maxA <= footprint_threshold] = np.nan

            zmin = self.im_scale(max_proj)[0]

            if max_pct is None:
                zmax = self.im_scale(max_proj, max_pct=self.im_scale(max_proj)[1])[1]
            else:
                zmax = self.im_scale(max_proj, max_pct=max_pct)[1]

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

    def plot_cell_reg(self,session_pair,image_list,max_pct=.95):  # only flexible for 2 sessions now
        '''
        (Notebook) Plot matched and non-matched cells across two sessions
        session_pair: indices of 2 sessions to plot together (i.e. to plot first two sessions [0,1])
        image_list: list of images for corresponding sessions
        max_pct
        returns: Plotly plot object
            one plot per session, registered cells in one color, other cells in another color
        '''
        reg_ind = self.get_reg_ind()
        S1 = session_pair[0]
        S2 = session_pair[1]
        pre_only = reg_ind[(reg_ind[:, S1] >= 0) & (reg_ind[:, S2] == -1)]
        post_only = reg_ind[(reg_ind[:, S2] >= 0) & (reg_ind[:, S1] == -1)]
        both = reg_ind[(reg_ind[:, S1] >= 0) & (reg_ind[:, S2] >= 0)]

        indices_list_pre = [both[:, 0], pre_only[:, 0]]
        indices_list_post = [both[:, 1], post_only[:, 1]]
        ticktext_pre = ['Both', '1 Only']
        ticktext_post = ['Both', '2 Only']
        colors_pre = ['#4682b4', '#663399']
        colors_post = ['#4682b4', '#b3dba0']

        indices_lists = [indices_list_pre, indices_list_post]
        ticktexts = [ticktext_pre, ticktext_post]
        colors_list = [colors_pre, colors_post]
        fig = self.plot_A_discrete_multisession(2, session_inds=session_pair, images_list=image_list,
                                                footprint_threshold=0, indices_lists=indices_lists, ticktexts=ticktexts,
                                                colors_list=colors_list,max_pct=max_pct)
        fig.update_layout(title='mouse: ' + self.animal + ' ' + self.FOV)
        fig.show(config={'scrollZoom': True})

    def plot_reg_pairs(self,session_inds, image_list, idx_list, min_pct='default', max_pct='default'):

        '''
        Notebook plot: plots grid of images from multiple session, with one cell matched cell pair overlaid,
                has an interactive slider to toggle between individual cells
        known bug: can only plot registered cells all together in one holomap or cells only active in one session in the same holomap.
                    if cell didnt have a match in CellReg found in a session it is not plotted.
        session_inds: list of indices for sessions to plot [i.e. for first two sessions [0,1])
        image_list: images to plot roi over, should be same order as footprints (i.e. footprints[0] correspond to session with image[0])
        roi_list: roi set indices that are which roi(s) to plot in each session

        :return: holoviews gridspace object
        '''
        hv.output(size=250)
        gridspace = hv.GridSpace(kdims=['Images', 'Session'], group='ROI', label='Neuron')
        footprints_list = self.footprints[session_inds]

        for j, im in enumerate(image_list):
            idxs = idx_list[j]
            holomap = hv.HoloMap(kdims='registration pair index')
            for k, idx in enumerate(idxs):
                panel = self.roi_plot(footprints_list[j], idx, im, min_pct=min_pct, max_pct=max_pct)
                holomap[k] = panel
                gridspace[0, j] = holomap

        roi_array = np.asarray(idx_list)
        d = {j: list(roi_array[:, j]) for j in np.arange(roi_array.shape[1])}

        return gridspace