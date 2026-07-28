import sys
# onep is installed via `pip install -e .` -- no sys.path shim needed
import pickle as pkl
import onep as op
import pandas as pd
from pathlib import Path

ddir = Path("Z:/Home/rsenne/dCA1_Clean_Data/Dill")
file = "collection_fc_allmice.pkl"

fp = ddir / file

with open(fp, 'rb') as f:
    collection = pkl.load(f)

for animal, obj in collection.animals.items():
    acc_cells = obj.accepted_traces
    # Save to CSV
    acc_cells.to_csv(Path(r"C:\Users\ryansenne\Downloads") / f"{animal}_fc_accepted_traces.csv", index=False)
    