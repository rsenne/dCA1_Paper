import tkinter.filedialog

import numpy as np
import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm
import matplotlib.pyplot as plt

__all__ = ["InscopixProcessing"]


class InscopixProcessing(CellReg_path = None):
    def __init__(self, filename):
        self.filename = filename
        self.all_cells = None
        self.rejected = None
        self.accepted = None

        self.CellReg_path = tkinter.filedialog.askdirectory("Select CellReg path")
    def read_inscopix(self):
        df = pd.read_csv(self.filename, header=[0, 1], index_col=0)
        # accepted needs a space because these files were saved poorly
        accepted_cells = df.xs(" accepted", axis=1, level=1)
        rejected_cells = df.xs(" rejected", axis=1, level=1)
        self.accepted = accepted_cells
        self.rejected = rejected_cells
        self.all_cells = df

    def classify_cells(self):
        pass

    def event_triggered_average(self):
        pass

