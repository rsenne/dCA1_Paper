import pandas as pd
import scipy.stats as stats
import numpy as np

csvs_a  = ['/Users/amonast/Desktop/dCA1_astro/Cell_Traces/astro3_traces/astro3_recall_traces_preprocess.csv',
        '/Users/amonast/Desktop/dCA1_astro/Cell_Traces/astro4_traces/astro4_recall_traces_preprocess.csv',
        '/Users/amonast/Desktop/dCA1_astro/Cell_Traces/astro5_traces/astro5_recall_traces_preprocess.csv',
        '/Users/amonast/Desktop/dCA1_astro/Cell_Traces/astro6_traces/astro6_recall_traces_preprocess.csv']

csvs_b = ['/Users/amonast/Desktop/dCA1_astro/Cell_Traces/astro7_traces/astro7_gen1_traces_preprocess.csv',
            '/Users/amonast/Desktop/dCA1_astro/Cell_Traces/astro8_traces/astro8_gen1_traces_preprocess.csv',
            '/Users/amonast/Desktop/dCA1_astro/Cell_Traces/astro9_traces/astro9_gen1_traces_preprocess.csv',
            '/Users/amonast/Desktop/dCA1_astro/Cell_Traces/astro10_traces/astro10_gen1_traces_preprocess.csv']

list_a = [pd.read_csv(file).drop('Unnamed: 0',axis=1) for file in csvs_a]
traces_a = pd.concat(list_a,axis=1)
traces_a

list_b = [pd.read_csv(file).drop('Unnamed: 0',axis=1) for file in csvs_b]
traces_b = pd.concat(list_b,axis=1)
traces_b


numpy_a= traces_a.T.iloc[:,:3303]
#Z-score your numpy array
numpy_za = stats.zscore(numpy_a, axis=1)
np.save('/Users/amonast/Desktop/dCA1_astro/recall_cxta_preprocessed_z.npy', numpy_za)


numpy_b = traces_b.T.iloc[:,:3303]
#Z-score your numpy array
numpy_zb = stats.zscore(numpy_b, axis=1)
np.save('/Users/amonast/Desktop/dCA1_astro/recall_cxtb_preprocessed_z.npy', numpy_zb)

