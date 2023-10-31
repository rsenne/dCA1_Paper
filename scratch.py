#%%
from onep.onephoton import InscopixProcessing

isx = InscopixProcessing('astro3','ext1',data_directory='/Users/amonast/Desktop/dCA1_astro')
df=isx.get_DLC_data()
# %%
