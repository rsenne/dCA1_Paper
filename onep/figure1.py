#%%
from onep import *
import holoviews as hv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sb
import matplotlib as mpl
import tifffile
hv.extension('bokeh')
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
from scipy.stats import zscore

mpl.use('TkAgg')
#%%
################# Fig 1C ################# representative traces
fc_astro = pd.read_csv('/Users/suthardr/Desktop/Cell_Traces/astro7_traces/astro7_gen1_traces.csv')
fc_astro_accepted = fc_astro.columns[fc_astro.isin([' accepted']).any()]
fc_astro = fc_astro[fc_astro_accepted]
traces = fc_astro.iloc[1:,:].values.astype(float)
zscored = zscore(traces,axis=0)
n=25
fig, axs = plt.subplots(n, 1, sharex='col', figsize=(10, 8))
for i in range(n):
    axs[i].plot(zscored[:4000,i], color='k')
    axs[i].axis('off')

fig.savefig('/Users/suthardr/Desktop/astro7_gen1_rep_fig1.png')
#%%
########## Figure 1E #############
## Number of astrocytes active ##

n_sessions =2
DF = pd.DataFrame()
for ani in ['astro3','astro4','astro5','astro6','astro7','astro8','astro9']:
    astro = cell_registration.CellReg(ani,'FOV1',n_sessions)
    footprints = astro.load_footprints_3D(affine_shifted=False)
    N_cells = [footprints[i].shape[0] for i in range(len(footprints))]
    series = pd.Series(N_cells)

    data = {'# Cells':series,'Animal':[ani]*n_sessions,'Group':[astro.group]*n_sessions,'Day':[0,1]}
    df = pd.DataFrame(data=data)
    DF = pd.concat([DF,df])

DF['Group_name']=DF['Group'].map({'EXT': 'CxtA', 'GEN': 'CxtB'})
# 
# ALL CELLS each session
font = {'family' : 'Arial',
        'weight' : 'normal',
        'size'   : 12}
mpl.rc('font',**font)
#%%
plt.figure(figsize=(3,4))

sb.pointplot(data=DF,x='Day',y='# Cells',hue='Group_name',errorbar='se',palette='Set2',hue_order=['CxtB','CxtA'])
plt.xlabel('Day',weight='normal',size=12)
plt.ylabel('# Astrocytes Active',weight='normal',size=12)
plt.gca().spines[['right', 'top']].set_visible(False)
plt.gca().spines[['left','bottom']].set_linewidth(2)
plt.gca().tick_params(width=2,labelsize=12)
plt.gca().legend().set_title('')
#
# plt.ylim([40,150])
# plt.hlines(y=115,xmin=0,xmax=3,color='k')
# plt.text(1.5,114,'*',size=18,ha='center')
# plt.hlines(y=125,xmin=0,xmax=2,color='k')
# plt.text(1,124,'*',size=18,ha='center')
# plt.hlines(y=135,xmin=0,xmax=1,color='k')
# plt.text(0.5,134,'**',size=18,ha='center')
plt.tight_layout()
plt.savefig('/Users/suthardr/Desktop/activecells.svg')
#%% stats 
import pingouin as pg
mix_anova = pg.mixed_anova(data=DF,dv='# Cells',between='Group',subject='Animal',within='Day')
posthoc = pg.pairwise_tests(data=DF,dv='# Cells',between='Group',within='Day',subject='Animal',padjust='fdr_bh')

#%%
############# Supplementary Figure 1 ################
############# EXT Group - FC Registrations ##########
n_sessions=2
animal = 'astro3'
astro = cell_registration.CellReg('astro3','FOV1',n_sessions)
inds = astro.load_registration_table().iloc[:,0:n_sessions].copy()
for col in inds.columns:
    inds[col]= inds[col].apply(np.int64) 

image_files = astro.get_summary_images(image_type='max dff',shifted=False)
images = [tifffile.imread(f) for f in image_files]
footprints = astro.load_footprints_3D(affine_shifted=False)

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
+ astro.rois_plot(session_ind=1,idxs=fc_matched[0],image=images[1])
# + astro.rois_plot(session_ind=0,idxs=fc_matched_fc[2],image=images[0]) \
# + astro.rois_plot(session_ind=0,idxs=fc_matched_fc[3],image=images[0]) \
# + astro.rois_plot(session_ind=2,idxs=fc_matched[1],image=images[2])\
# + astro.rois_plot(session_ind=3,idxs=fc_matched[2],image=images[3])\
# + astro.rois_plot(session_ind=4,idxs=fc_matched[3],image=images[4])
layout.cols(4)

hv.save(layout,f"/Users/suthardr/Desktop/fc_overlap_fovs_{animal}.png")
#%%
################ GEN group - FC registrations ####################
n_sessions=5
animal = 'astro8'
astro = cell_registration.CellReg(animal,'FOV1',n_sessions)
inds = astro.load_registration_table().iloc[:,0:n_sessions].copy()
for col in inds.columns:
    inds[col]= inds[col].apply(np.int64) 

image_files = astro.get_summary_images(image_type='max dff',shifted=False)
images = [tifffile.imread(f) for f in image_files]
footprints = astro.load_footprints_3D(affine_shifted=False)

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

color_discrete_sequence = ['rgb(255,255,255)']+px.colors.qualitative.Set2

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

##%% pie charts
traces=[]
sessions=['Recall', 'Ext1','Ext2','Ext3']
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
                            domain={'x': [X[i][0],X[i][1]], 'y': [0.0, 1]},
                            marker=dict(colors=color_discrete_sequence),
                            textfont=dict(size=25, color='#000000'))
    traces.append(trace)

layout = go.Layout(height = 600,width = 1200,autosize = False)
fig = go.Figure(data = traces,layout=layout)
fig.show()

fig.write_image("/Users/amonast/Desktop/dCA1_astro/Figures/EXT_donuts_allcells.png",scale=2)
#%%
######## Gen Group Pie charts #############
n_sessions=5
animals = ['astro7','astro8','astro9']
all_overlap=[]
all_cells = []
all_stable = []

color_discrete_sequence = ['rgb(255,255,255)']+px.colors.qualitative.Dark2
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
#%% pie charts 
traces=[]
sessions=['Neutral1', 'Neutral2','Neutral3','Neutral4']
X=[(0, 0.25), (0.25, 0.5), (0.5, 0.75), (0.75, 1.0)]
for i in range(n_sessions-1):

    session = sessions[i]
    # data for px.sunburst
    data = dict(labels=[" ", "FC Overlap", session+" only", "Stable"],
                parent=["", " ", " ", "FC Overlap" ],
                value=[0, cells_arr[i]-overlaps_arr[i], overlaps_arr[i], stable_n])

    # extract data and structure FROM px.sunburst
    sb = px.sunburst(data,
                    names='labels',
                    parents='parent',
                    values='value')._data

    # traces with separate domains to form a subplot
    trace = go.Sunburst(labels=sb[0]['labels'],
                            parents=sb[0]['parents'],
                            values=sb[0]['values'],
                            domain={'x': [X[i][0],X[i][1]], 'y': [0.0, 1]},
                            marker=dict(colors=color_discrete_sequence),
                            textfont=dict(size=25, color='#000000'))
    
    traces.append(trace)
layout = go.Layout(height = 600,
                   width = 1200,
                   autosize = False)
fig = go.Figure(data = traces,layout=layout)
fig.show()

fig.write_image("/Users/amonast/Desktop/dCA1_astro/Figures/GEN_donuts_allcells.png",scale=2)
# %% ###### percentages ######
n_sessions=5
animals = ['astro7','astro8','astro9']
all_overlap=[]
all_cells = []
all_stable = []

color_discrete_sequence = ['rgb(255,255,255)']+px.colors.qualitative.Dark2
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

props_stable  = [all_stable[ani]/all_cells[ani] for ani in range(len(animals))]
props_fc = [all_overlap[ani]/all_overlap[ani] for ani in range(len(animals))]
#%% Bar charts 
n_sessions=2
animals = ['astro3','astro4', 'astro5','astro6', 'astro7','astro8','astro9']
DF = pd.DataFrame()
for ani in animals:
    astro = cell_registration.CellReg(animal=ani,fov='FOV1',N_sessions=n_sessions)
    overlaps = astro.load_registration_table().iloc[0,n_sessions:].values.astype(int)

    #get total num cells for every session
    n_cells=[]
    session_only_all=[]
    for s in range(n_sessions-1):
        session=s+1
        sn_cells = astro.load_footprints_3D(affine_shifted=False)[session].shape[0]
        n_cells.append(sn_cells)
        session_only = sn_cells - overlaps[s]
        session_only_all.append(session_only)

        # print('total cells'+str(sn_cells))
        # print('fc overlap cells'+str(overlaps[s]))
        # print('session only'+str(session_only))
    
    df = pd.DataFrame()
    df['Animal'] = [ani]*4
    df['Group'] = [astro.group]*4
    df['Day'] = ['Day1','Day2']
    df['Session'] = astro.sessions[1:]
    df['# Cells'] = n_cells
    df['% Overlap FC'] =overlaps/np.array(n_cells)*100
    df['% Non-overlap'] = np.array(session_only_all)/np.array(n_cells)*100
    DF = pd.concat([DF,df])

sb.barplot(data=DF,hue='Group',x='Day',y='% Overlap FC',errorbar='se')
sb.swarmplot(data=DF,dodge=True,hue='Group',x='Day',y='% Overlap FC')
    # get # of overlaps with FC(Day0); 1x4 array - get from first row of csv

