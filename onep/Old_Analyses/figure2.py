#%%
import matplotlib.pyplot as plt
import numpy as np

#%%
ix = onephoton.InscopixProcessing(filename='/Users/amonast/Desktop/dCA1_astro/Cell_Traces/astro5_traces/astro5_fc_traces.csv', animal='astro5')
ix.read_inscopix()
traces = ix.accepted.values

times = ix.accepted.index.values
shocks = [120,180,240,300]
#%%
t_inds = []
for shock in shocks:
    shock_i = np.argmin(np.abs(times-shock))
    plt.plot(np.abs(times-shock))
    t_inds.append(shock_i)
#%%
n=15
fig, axs = plt.subplots(n+1, 1, sharex='col', figsize=(10, 8))

for i in range(1,n+1):
    axs[i].plot(zscore(traces[:,i]), color='k')
    axs[i].axis('off')

for t in t_inds:
    axs[0].plot(t,10,'rv',markersize=15)
axs[0].axis('off')

fig.savefig('/Users/amonast/Desktop/dCA1_astro/astro5_fc_rep_fig2.png')
# %%
