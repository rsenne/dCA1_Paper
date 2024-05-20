#%%
from onep import *
import holoviews as hv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sb
import matplotlib as mpl
mpl.use('TkAgg')

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
# # ALL CELLS each session
# font = {'family' : 'Arial',
#         'weight' : 'bold',
#         'size'   : 10}
# mpl.rc('font',**font)
#%% ALL CELLS each session

# plt.figure(figsize=(3,4))
#
# sb.pointplot(data=DF,x='Day',y='# Cells',hue='Group_name',errorbar='se',palette='Set2',hue_order=['CxtB','CxtA'])
# plt.xlabel('Day',weight='regular',size=12)
# plt.ylabel('# Astrocytes Active',weight='regular',size=12)
# plt.gca().spines[['right', 'top']].set_visible(False)
# plt.gca().spines[['left','bottom']].set_linewidth(2)
# plt.gca().tick_params(width=2,labelsize=12)
# plt.gca().legend().set_title('')
#
# plt.tight_layout()
# plt.savefig('/Users/suthardr/Desktop/activecells.svg')

#%% TOTAL CELLS
DF = pd.read_csv('/Users/suthardr/Desktop/NEW_dCA1_ANALYSIS/reactivated_heatmaps/total_cells.csv')
plt.figure(figsize=(3,4))

sb.pointplot(data=DF,x='Day',y='Total_cells',hue='Group_name',errorbar='se',palette='Set2',hue_order=['CxtB','CxtA'])
plt.xlabel('Day',weight='regular',size=12)
plt.ylabel('# Astrocytes Active',weight='regular',size=12)
plt.gca().spines[['right', 'top']].set_visible(False)
plt.gca().spines[['left','bottom']].set_linewidth(2)
plt.gca().tick_params(width=2,labelsize=12)
plt.gca().legend().set_title('')

plt.tight_layout()

plt.savefig('/Users/suthardr/Desktop/total_cells.svg')

#%% REACTIVATED CELLS
DF = pd.read_csv('/Users/suthardr/Desktop/reactivated_cells.csv')
plt.figure(figsize=(3,4))
sb.boxplot(data=DF,x='Group_name',y='% Reactivated',palette='Set2',hue_order=['CxtB','CxtA'])
sb.stripplot(x='Group_name', y='% Reactivated', data=DF,
              size=4, linewidth=0.3, color='grey', edgecolor='black', dodge=True, jitter=False)
plt.xlabel('Day',weight='regular',size=12)
plt.ylabel('% Reactivated Cells',weight='regular',size=12)
plt.gca().spines[['right', 'top']].set_visible(False)
plt.gca().spines[['left','bottom']].set_linewidth(2)
plt.gca().tick_params(width=2,labelsize=12)

plt.tight_layout()
plt.savefig('/Users/suthardr/Desktop/%reactivatedcells_box.svg')

##### Figure 1F #####
#%% % of cells overlap with FC for each day, (combine all cells from animals within group)

astro = cell_registration.CellReg('astro3','FOV1',n_sessions)
inds = astro.load_registration_table().iloc[:,0:n_sessions]
for col in inds.columns:
    inds[col]= inds[col].apply(np.int64) #wrong
#%%
group = ['astro3']
session_only = [0, 0, 0, 0]
session_overlap = [0, 0, 0, 0]
stable_overlap = 0
for annie in group:
    astro_tables = cell_registration.CellReg(annie,'FOV1',n_sessions)
    inds = astro_tables.load_registration_table().iloc[:, 0:n_sessions]
    for i in range(len(inds['fc'])):
        if inds['fc'][i] >= 0 and inds['recall'][i] >= 0:
            session_overlap[0] += 1
        if inds['fc'][i] == -1 and inds['recall'][i] >= 0:
            session_only[0] += 1
        if inds['fc'][i] >= 0 and inds['EXT1'][i] >= 0:
            session_overlap[1] += 1
        if inds['fc'][i] == -1 and inds['EXT1'][i] >= 0:
            session_only[1] += 1
        if inds['fc'][i] >= 0 and inds['EXT2'][i] >= 0:
            session_overlap[2] += 1
        if inds['fc'][i] == -1 and inds['EXT2'][i] >= 0:
            session_only[2] += 1
        if inds['fc'][i] >= 0 and inds['EXT3'][i] >= 0:
            session_overlap[3] += 1
        if inds['fc'][i] == -1 and inds['EXT3'][i] >= 0:
            session_only[3] += 1
        if inds['fc'][i] >= 0 and inds['recall'][i] >= 0 and inds['EXT1'][i] >= 0 and inds['EXT2'][i] >= 0 and inds['EXT3'][i] >= 0:
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
group = ['astro9']
n_sessions = 2
fc_only = [0]
recall_only = [0]
overlap = [0]
# stable_overlap = 0
for annie in group:
    astro_tables = cell_registration.CellReg(annie,'FOV1',n_sessions)
    inds = astro_tables.load_registration_table().iloc[:, 0:n_sessions]
    for i in range(len(inds.iloc[:,0])):
        if inds.iloc[:,0][i] >= 0 and inds.iloc[:,1][i] >= 0:
            overlap[0] += 1
        if inds.iloc[:,0][i] == -1 and inds.iloc[:,1][i] >= 0:
            recall_only[0] += 1
        if inds.iloc[:,0][i] >= 0 and inds.iloc[:,1][i] == -1:
            fc_only[0] += 1
        # if inds['fc'][i] >= 0 and inds['GEN2'][i] >= 0:
        #     session_overlap[1] += 1
        # if inds['fc'][i] == -1 and inds['GEN2'][i] >= 0:
        #     session_only[1] += 1
        # if inds['fc'][i] >= 0 and inds['GEN3'][i] >= 0:
        #     session_overlap[2] += 1
        # if inds['fc'][i] == -1 and inds['GEN3'][i] >= 0:
        #     session_only[2] += 1
        # if inds['fc'][i] >= 0 and inds['GEN4'][i] >= 0:
        #     session_overlap[3] += 1
        # if inds['fc'][i] == -1 and inds['GEN4'][i] >= 0:
        #     session_only[3] += 1
        # if inds['fc'][i] >= 0 and inds['GEN1'][i] >= 0:
        #         # and inds['GEN2'][i] >= 0 and inds['GEN3'][i] >= 0 and inds['GEN4'][i] >= 0:
        #     stable_overlap += 1
print(fc_only)
print(overlap)
print(recall_only)

n = 1
r = np.arange(n)
width = 0.25

plt.figure(figsize=(4,3))

plt.bar(r, fc_only, color='coral',
        width=width, edgecolor='black',
        label='FC Session Only')
plt.bar(r + width, overlap, color='mediumaquamarine',
        width=width, edgecolor='black',
        label='Overlap: FC-Recall')
plt.bar(r + 2*width, recall_only, color='mediumpurple',
        width=width, edgecolor='black',
        label='Recall Session Only')

plt.xlabel("Astro9")
plt.ylabel("Number of Cells")
plt.title("Longitudinal Registration")

# plt.grid(linestyle='--')
# plt.xticks(r + width / 2, ['FC_GEN1', 'FC_Gen2'])
plt.legend(loc='upper left')
plt.tight_layout()
plt.show()


