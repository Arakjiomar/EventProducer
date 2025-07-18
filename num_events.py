import uproot
import glob

#Change the path and pattern to match your ttyy files
file_pattern = "/eos/home-o/oarakji/tth/myRoot/fcc_v07/II/mgp8_pp_ttaa01j_5f_50TeV/events_*.root"

files = glob.glob(file_pattern)
total_events = 0

for fname in files:
    with uproot.open(fname) as f:
        tree = f["events"]
        n_events = tree.num_entries
        print(f"{fname}: {n_events} events")
        total_events += n_events

print(f"Total ttyy events: {total_events}")

# file_pattern = "/eos/home-o/oarakji/tth/myRoot/fcc_v07/II/mgp8_pp_vbf_h01j_5f_50TeV/events_*.root"

# files = glob.glob(file_pattern)
# total_events = 0

# for fname in files:
#     with uproot.open(fname) as f:
#         tree = f["events"]
#         n_events = tree.num_entries
#         print(f"{fname}: {n_events} events")
#         total_events += n_events

# print(f"Total vbf events: {total_events}")

file_pattern = "/eos/home-o/oarakji/tth/myRoot/fcc_v07/II/mgp8_pp_vh012j_5f_50TeV/events_*.root"

files = glob.glob(file_pattern)
total_events = 0

for fname in files:
    with uproot.open(fname) as f:
        tree = f["events"]
        n_events = tree.num_entries
        print(f"{fname}: {n_events} events")
        total_events += n_events

print(f"Total vh events: {total_events}")

file_pattern = "/eos/home-o/oarakji/tth/myRoot/fcc_v07/II/mgp8_pp_tth01j_5f_50TeV/events_*.root"

files = glob.glob(file_pattern)
total_events = 0

for fname in files:
    with uproot.open(fname) as f:
        tree = f["events"]
        n_events = tree.num_entries
        print(f"{fname}: {n_events} events")
        total_events += n_events

print(f"Total tth events: {total_events}")

file_pattern = "/eos/home-o/oarakji/tth/myRoot/fcc_v07/II/mgp8_pp_th12j_5f_50TeV/events_*.root"

files = glob.glob(file_pattern)
total_events = 0

for fname in files:
    with uproot.open(fname) as f:
        tree = f["events"]
        n_events = tree.num_entries
        print(f"{fname}: {n_events} events")
        total_events += n_events

print(f"Total tth events: {total_events}")