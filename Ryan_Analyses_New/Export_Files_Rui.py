import pickle as pkl
import onep as op
import pandas as pd
from pathlib import Path

ddir = r"C:\Users\ryansenne\Desktop\Dill"
file = "collection_hab_allmice.pkl"

fp = Path(ddir) / file

with open(fp, 'rb') as f:
    collection = pkl.load(f)

for animal, obj in collection.animals.items():
    acc_cells = obj.accepted_traces
    # Save to CSV
    acc_cells.to_csv(Path(ddir) / f"{animal}_hab_accepted_traces.csv", index=False)
    