#%%
import matplotlib.pyplot

from onep import *
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
n_sessions = 5

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

astro = cell_registration.CellReg('astro3','FOV1',n_sessions)
inds = astro.load_registration_table().iloc[:,0:n_sessions]
for col in inds.columns:
    inds[col]= inds[col].apply(np.int64) #wrong
#%%
group = ['astro3', 'astro5']
session_only = [0, 0, 0, 0]
session_overlap = [0, 0, 0, 0]
stable_overlap = 0
for annie in group:
    astro_tables = cell_registration.CellReg(annie,'FOV1',n_sessions)
    inds = astro_tables.load_registration_table().iloc[:, 0:n_sessions]
    for i in range(len(inds['FC'])):
        if inds['FC'][i] >= 0 and inds['Recall'][i] >= 0:
            session_overlap[0] += 1
        if inds['FC'][i] == -1 and inds['Recall'][i] >= 0:
            session_only[0] += 1
        if inds['FC'][i] >= 0 and inds['EXT1'][i] >= 0:
            session_overlap[1] += 1
        if inds['FC'][i] == -1 and inds['EXT1'][i] >= 0:
            session_only[1] += 1
        if inds['FC'][i] >= 0 and inds['EXT2'][i] >= 0:
            session_overlap[2] += 1
        if inds['FC'][i] == -1 and inds['EXT2'][i] >= 0:
            session_only[2] += 1
        if inds['FC'][i] >= 0 and inds['EXT3'][i] >= 0:
            session_overlap[3] += 1
        if inds['FC'][i] == -1 and inds['EXT3'][i] >= 0:
            session_only[3] += 1
        if inds['FC'][i] >= 0 and inds['Recall'][i] >= 0 and inds['EXT1'][i] >= 0 and inds['EXT2'][i] >= 0 and inds['EXT3'][i] >= 0:
            stable_overlap += 1
print(session_only)
print(session_overlap)
print(stable_overlap)

n = 4
r = np.arange(n)
width = 0.25

plt.figure(figsize=(8,6))

plt.bar(r, session_only, color='coral',
        width=width, edgecolor='black',
        label='Comparison Session Only')
plt.bar(r + width, session_overlap, color='mediumaquamarine',
        width=width, edgecolor='black',
        label='Overlap with FC')
plt.bar(r + 2*width, stable_overlap, color='mediumpurple',
        width=width, edgecolor='black',
        label='Stable Overlap All Sessions')

plt.xlabel("Session Comparisons")
plt.ylabel("Number of Cells")
plt.title("Longitudinal Registration Through Extinction")

# plt.grid(linestyle='--')
plt.xticks(r + width / 2, ['FC_Recall', 'FC_EXT1', 'FC_EXT2', 'FC_EXT3'])
plt.legend(loc='upper left')
#plt.tight_layout()
plt.show()



#%%
group = ['astro7', 'astro8','astro9']
session_only = [0, 0, 0, 0]
session_overlap = [0, 0, 0, 0]
stable_overlap = 0
for annie in group:
    astro_tables = cell_registration.CellReg(annie,'FOV1',n_sessions)
    inds = astro_tables.load_registration_table().iloc[:, 0:n_sessions]
    for i in range(len(inds.iloc[:,0])):
        if inds.iloc[:,0][i] >= 0 and inds['GEN1'][i] >= 0:
            session_overlap[0] += 1
        if inds['FC'][i] == -1 and inds['GEN1'][i] >= 0:
            session_only[0] += 1
        if inds['FC'][i] >= 0 and inds['GEN2'][i] >= 0:
            session_overlap[1] += 1
        if inds['FC'][i] == -1 and inds['GEN2'][i] >= 0:
            session_only[1] += 1
        if inds['FC'][i] >= 0 and inds['GEN3'][i] >= 0:
            session_overlap[2] += 1
        if inds['FC'][i] == -1 and inds['GEN3'][i] >= 0:
            session_only[2] += 1
        if inds['FC'][i] >= 0 and inds['GEN4'][i] >= 0:
            session_overlap[3] += 1
        if inds['FC'][i] == -1 and inds['GEN4'][i] >= 0:
            session_only[3] += 1
        if inds['FC'][i] >= 0 and inds['GEN1'][i] >= 0 and inds['GEN2'][i] >= 0 and inds['GEN3'][i] >= 0 and inds['GEN4'][i] >= 0:
            stable_overlap += 1
print(session_only)
print(session_overlap)
print(stable_overlap)

n = 4
r = np.arange(n)
width = 0.25

plt.figure(figsize=(8,6))

plt.bar(r, session_only, color='coral',
        width=width, edgecolor='black',
        label='Comparison Session Only')
plt.bar(r + width, session_overlap, color='mediumaquamarine',
        width=width, edgecolor='black',
        label='Overlap with FC')
plt.bar(r + 2*width, stable_overlap, color='mediumpurple',
        width=width, edgecolor='black',
        label='Stable Overlap All Sessions')

plt.xlabel("Session Comparisons")
plt.ylabel("Number of Cells")
plt.title("Longitudinal Registration During Generalization")

# plt.grid(linestyle='--')
plt.xticks(r + width / 2, ['FC_GEN1', 'FC_GEN2', 'FC_GEN3', 'FC_GEN4'])
plt.legend(loc='upper left')
#plt.tight_layout()
plt.show()


