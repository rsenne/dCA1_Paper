#%%
from onephoton import *
import holoviews as hv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sb
import matplotlib as mpl
# mpl.use('TkAgg')
#%%
##### Figure 1E########
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
#%% ALL CELLS each session

font = {'family' : 'Arial',
        'weight' : 'bold',
        'size'   : 10}
mpl.rc('font',**font)

plt.figure(figsize=(3,3))
sb.lineplot(data=DF,x='Day',y='# Cells',hue='Group',err_style='bars')
plt.xlabel('Day')
plt.ylabel('# Astrocytes Active')
plt.tight_layout()


#%%
##### Figure 1F #####
#%% % of cells overlap with FC for each day, (combine all cells from animals within group)

astro = cell_registration.CellReg('astro5','FOV1',n_sessions)
inds = astro.load_registration_table().iloc[:,0:n_sessions]
for col in inds.columns:
    inds[col]= inds[col].apply(np.int64) #wrong
#%%
# do this separately for each group
# for each day (D1-D4)
    # for each animal
        # get # of overlaps with FC(Day0); 1x4 array - get from first row of csv
        #append it to some list or array A

        # get # cells that have index in all the columns

    # sum cells each day A across animals & get proportion that overlaps with FC
    # labels = 'Overlap w FC', 'New Cells'
    # plot pie chart for that day


#### Figure 1G ### stable population of cells across all days for each group
# pie chart or what