import uproot

with uproot.open("/eos/home-o/oarakji/tth/myRoot/fcc_v07/II/mgp8_pp_tth01j_5f_50TeV/events_001033803.root") as f:
    tree = f["events"]  # or the correct tree name
    weights = tree["EventHeader.weight"].array(library="np")
    print(weights[:100])  # print first 100 weights