#%%
from onephoton import *
import holoviews as hv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sb
import matplotlib as mpl
import tifffile
hv.extension('bokeh')
import plotly
import plotly.offline as py
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
# mpl.use('TkAgg')
#%%
########## Figure 1E #############
## Number of astrocytes active ##
#%%
n_sessions =5
DF = pd.DataFrame()
for ani in ['astro3','astro4','astro5','astro6','astro7','astro8','astro9','astro10']:
    astro = cell_registration.CellReg(ani,'FOV1',n_sessions)
    footprints = astro.load_footprints_3D(affine_shifted=False)
    N_cells = [footprints[i].shape[0] for i in range(len(footprints))]
    series = pd.Series(N_cells)

    data = {'# Cells':series,'Animal':[ani]*n_sessions,'Group':[astro.group]*n_sessions,'Day':[0,1,2,3,4]}
    df = pd.DataFrame(data=data)
    DF = pd.concat([DF,df])
# 
# ALL CELLS each session
font = {'family' : 'Arial',
        'weight' : 'bold',
        'size'   : 10}
mpl.rc('font',**font)

plt.figure(figsize=(3,4))
#sb.lineplot(data=DF,x='Day',y='# Cells',hue='Group',err_style='bars')
sb.pointplot(data=DF,x='Day',y='# Cells',hue='Group',errorbar='se')
plt.xlabel('Day',weight='bold')
plt.ylabel('# Astrocytes Active',weight='bold')
plt.tight_layout()
plt.savefig('/Users/amonast/Desktop/dCA1_astro/Figures/all_cells.png')
#%%
############# Supplementary Figure 1 ################
############# EXT Group - FC Registrations ##########
n_sessions=5
animal = 'astro5'
astro = cell_registration.CellReg('astro5','FOV1',n_sessions)
inds = astro.load_registration_table().iloc[:,0:n_sessions].copy()
for col in inds.columns:
    inds[col]= inds[col].apply(np.int64) 

image_files = astro.get_summary_images(image_type='max dff',shifted=True)
images = [tifffile.imread(f) for f in image_files]
footprints = astro.load_footprints_3D(affine_shifted=True)

fc_matched = []
fc_matched_fc = []
fc_matched_foots = []
for i in range(n_sessions-1):
    s = i+1
    inds_reg = inds[s].loc[(inds[0]!=-1)&(inds[s]!=-1)].values
    fc_matched.append(inds_reg)
    inds_fc = inds[0].loc[(inds[0]!=-1)&(inds[s]!=-1)].values
    fc_matched_fc.append(inds_fc)
    foots = footprints[s].sum(axis=0)
    fc_matched_foots.append(foots)

layout = astro.rois_plot(session_ind=0,idxs=fc_matched_fc[0],image=images[0])\
+ astro.rois_plot(session_ind=0,idxs=fc_matched_fc[1],image=images[0]) \
+ astro.rois_plot(session_ind=0,idxs=fc_matched_fc[2],image=images[0]) \
+ astro.rois_plot(session_ind=0,idxs=fc_matched_fc[3],image=images[0]) \
+ astro.rois_plot(session_ind=1,idxs=fc_matched[0],image=images[1]) \
+ astro.rois_plot(session_ind=2,idxs=fc_matched[1],image=images[2])\
+ astro.rois_plot(session_ind=3,idxs=fc_matched[2],image=images[3])\
+ astro.rois_plot(session_ind=4,idxs=fc_matched[3],image=images[4])
layout.cols(4)

hv.save(layout,f"/Users/amonast/Desktop/dCA1_astro/Figures/fc_overlap_fovs_{animal}.png")
#%%
################ GEN group - FC registrations ####################
n_sessions=5
animal = 'astro8'
astro = cell_registration.CellReg(animal,'FOV1',n_sessions)
inds = astro.load_registration_table().iloc[:,0:n_sessions].copy()
for col in inds.columns:
    inds[col]= inds[col].apply(np.int64) 

image_files = astro.get_summary_images(image_type='max dff',shifted=True)
images = [tifffile.imread(f) for f in image_files]
footprints = astro.load_footprints_3D(affine_shifted=True)

fc_matched = []
fc_matched_fc = []
fc_matched_foots = []
for i in range(n_sessions-1):
    s = i+1
    inds_reg = inds[s].loc[(inds[0]!=-1)&(inds[s]!=-1)].values
    fc_matched.append(inds_reg)
    inds_fc = inds[0].loc[(inds[0]!=-1)&(inds[s]!=-1)].values
    fc_matched_fc.append(inds_fc)
    foots = footprints[s].sum(axis=0)
    fc_matched_foots.append(foots)

layout = astro.rois_plot(session_ind=0,idxs=fc_matched_fc[0],image=images[0])\
+ astro.rois_plot(session_ind=0,idxs=fc_matched_fc[1],image=images[0]) \
+ astro.rois_plot(session_ind=0,idxs=fc_matched_fc[2],image=images[0]) \
+ astro.rois_plot(session_ind=0,idxs=fc_matched_fc[3],image=images[0]) \
+ astro.rois_plot(session_ind=1,idxs=fc_matched[0],image=images[1]) \
+ astro.rois_plot(session_ind=2,idxs=fc_matched[1],image=images[2])\
+ astro.rois_plot(session_ind=3,idxs=fc_matched[2],image=images[3])\
+ astro.rois_plot(session_ind=4,idxs=fc_matched[3],image=images[4])
layout.cols(4)

hv.save(layout,f"/Users/amonast/Desktop/dCA1_astro/Figures/fc_overlap_fovs_{animal}.png")

###########################################
#%%
###########################################
################## Figure 1E Pie Charts ########################
########### EXT Group Pie Charts ###############
n_sessions=5
animals = ['astro3','astro5']
all_overlap=[]
all_cells = []
all_stable = []
for ani in animals:
    astro = cell_registration.CellReg(animal=ani,fov='FOV1',N_sessions=n_sessions)
        
    #get total num cells for every session
    n_cells=[]
    for s in range(n_sessions-1):
        session=s+1
        sn_cells = astro.load_footprints_3D(affine_shifted=True)[session].shape[0]
        n_cells.append(sn_cells)
        
    # get # of overlaps with FC(Day0); 1x4 array - get from first row of csv
    overlaps = astro.load_registration_table().iloc[0,n_sessions:].values.astype(int)

    #get stable number across all days 
    inds = astro.load_registration_table().iloc[:,0:n_sessions].copy()
    stable = inds.loc[(inds[0]!=-1) & (inds[1]!=-1) & (inds[2]!=-1) & (inds[3]!=-1) & (inds[4]!=-1)].shape[0]
    
    #store all values for this animal
    all_stable.append(stable)
    all_overlap.append(overlaps) #append it to some list or array A
    all_cells.append(n_cells)

# sum across animals
overlaps_arr = np.array(all_overlap).sum(axis=0) 
cells_arr = np.array(all_cells).sum(axis=0)
stable_n = np.sum(all_stable)

traces=[]
sessions=astro.sessions[1:]
X=[(0, 0.25), (0.25, 0.5), (0.5, 0.75), (0.75, 1.0)]
for i in range(n_sessions-1):

    session = sessions[i]
    # data for px.sunburst
    data = dict(labels=[" ", "FC Overlap", session+" only", "Stable"],
                parent=["", " ", " ", "FC Overlap" ],
                value=[0, cells_arr[i]-overlaps_arr[i], overlaps_arr[i], stable_n])

    # extract data and structure FROM px.sunburst
    sb =px.sunburst(data,
                    names='labels',
                    parents='parent',
                    values='value',
                    )._data

    # traces with separate domains to form a subplot
    trace = go.Sunburst(labels=sb[0]['labels'],
                            parents=sb[0]['parents'],
                            values=sb[0]['values'],
                            domain={'x': [X[i][0],X[i][1]], 'y': [0.0, 1]})
    
    traces.append(trace)

layout = go.Layout(height = 600,
                   width = 600,
                   autosize = False,
                   title = 'Side by side px.Sunburst diagrams')
fig = go.Figure(data = traces)
fig.show()

fig.write_image("/Users/amonast/Desktop/dCA1_astro/Figures/EXT_donuts_allcells.png",scale=2)
#%%
######## Gen Group Pie charts #############
n_sessions=5
animals = ['astro7','astro8','astro9']
all_overlap=[]
all_cells = []
all_stable = []

for ani in animals:
    astro = cell_registration.CellReg(animal=ani,fov='FOV1',N_sessions=n_sessions)
        
    #get total num cells for every session
    n_cells=[]
    for s in range(n_sessions-1):
        session=s+1
        sn_cells = astro.load_footprints_3D(affine_shifted=True)[session].shape[0]
        n_cells.append(sn_cells)
        
    # get # of overlaps with FC(Day0); 1x4 array - get from first row of csv
    overlaps = astro.load_registration_table().iloc[0,n_sessions:].values.astype(int)

    #get stable number across all days 
    inds = astro.load_registration_table().iloc[:,0:n_sessions].copy()
    stable = inds.loc[(inds[0]!=-1) & (inds[1]!=-1) & (inds[2]!=-1) & (inds[3]!=-1) & (inds[4]!=-1)].shape[0]
    
    #store all values for this animal
    all_stable.append(stable)
    all_overlap.append(overlaps) #append it to some list or array A
    all_cells.append(n_cells)

# sum across animals
overlaps_arr = np.array(all_overlap).sum(axis=0) 
cells_arr = np.array(all_cells).sum(axis=0)
stable_n = np.sum(all_stable)

traces=[]
sessions=astro.sessions[1:]
X=[(0, 0.25), (0.25, 0.5), (0.5, 0.75), (0.75, 1.0)]
for i in range(n_sessions-1):

    session = sessions[i]
    # data for px.sunburst
    data = dict(labels=[" ", "FC Overlap", session+" only", "Stable"],
                parent=["", " ", " ", "FC Overlap" ],
                value=[0, cells_arr[i]-overlaps_arr[i], overlaps_arr[i], stable_n])

    # extract data and structure FROM px.sunburst
    sb =px.sunburst(data,
                    names='labels',
                    parents='parent',
                    values='value',
                    )._data

    # traces with separate domains to form a subplot
    trace = go.Sunburst(labels=sb[0]['labels'],
                            parents=sb[0]['parents'],
                            values=sb[0]['values'],
                            domain={'x': [X[i][0],X[i][1]], 'y': [0.0, 1]})
    
    traces.append(trace)
layout = go.Layout(height = 600,
                   width = 600,
                   autosize = False,
                   title = 'Side by side px.Sunburst diagrams')
fig = go.Figure(data = traces)
fig.show()

fig.write_image("/Users/amonast/Desktop/dCA1_astro/Figures/GEN_donuts_allcells.png",scale=2)
# %%
