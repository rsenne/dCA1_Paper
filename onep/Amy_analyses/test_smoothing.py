#%%
from onephoton import dCA1Group,InscopixProcessing
import matplotlib.pyplot as plt
import os 
# A_ani = ['astro3','astro4','astro5','astro6']
# B_ani = 'astro7','astro8','astro9','astro10'

#%%
def main():
    A_sessions = ['ext1','ext2','ext3']
    B_sessions = ['gen2','gen3','gen4']
    data_dir = '/Users/amonast/Desktop/dCA1_astro'
    for sessions in zip(A_sessions,B_sessions):
        a = sessions[0]
        b = sessions[1]

        grpA = dCA1Group(InscopixProcessing('astro3',a,data_dir),
                        InscopixProcessing('astro4',a,data_dir),
                        InscopixProcessing('astro5',a,data_dir),
                        InscopixProcessing('astro6',a,data_dir))
        grpA.preprocess()
        
        grpB = dCA1Group(InscopixProcessing('astro7',b,data_dir),
                        InscopixProcessing('astro8',b,data_dir),
                        InscopixProcessing('astro9',b,data_dir),
                        InscopixProcessing('astro10',b,data_dir))
        grpB.preprocess()

        grpA.save_processed_traces(savepath=os.path.join(data_dir,'Cell_Traces'))
        grpB.save_processed_traces(savepath=os.path.join(data_dir,'Cell_Traces'))

##### example data
#%%

def plot_examples(n_cells,range_cells):
    data_dir = '/Users/amonast/Desktop/dCA1_astro'
    ext_group = dCA1Group(InscopixProcessing('astro3','fc',data_dir),
                        InscopixProcessing('astro4','fc',data_dir),
                        InscopixProcessing('astro5','fc',data_dir),
                        InscopixProcessing('astro6','fc',data_dir))
    traces_raw = ext_group.grab_all_traces() #grab uncorrected traces
    ext_group.preprocess() # preprocess: overwrites the smoothed traces
    traces = ext_group.grab_all_traces() #

    ##plot examples
    for i in range(0,n_cells,int(round(range_cells/n_cells))):
        plt.figure()
        plt.plot(traces_raw[i])
        plt.plot(traces[i])
        plt.hlines(0,0,round(traces.index[-1]),color='k',linestyle='dotted',linewidth=2)

if __name__=='__main__':
    main()