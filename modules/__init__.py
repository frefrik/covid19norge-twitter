import os
from .utils import update_data

# Create datadirs
datadirs = ["./data", "./graphs"]

for datadir in datadirs:
    if not os.path.exists(datadir):
        os.makedirs(datadir)

# Create and update datafiles if not exist
filenames = ["tested", "confirmed", "dead", "admissions", "respiratory"]

for filename in filenames:
    if os.path.isfile("./data/" + filename + ".txt"):
        pass
    else:
        print("Datafile for " + filename + " missing. Creating file with latest data.")
        update_data(filename)
