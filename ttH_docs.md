# Documentation for ttH samples @ 50 TeV

## Generate LHE files directly from MG5
=====================================

To send jobs directly from MG5, you need a configuration file (see in ```mg5/examples``` directory ```*.mg5```) and, optionally:
   - a ```cuts.f``` file (containing additional cuts)
   - a model (see in ```models``` directory for instance)

**N.B.** At the moment no example is generated for FCC-ee this way. Below is an example for FCC-hh.

As before, you need to add the process to the ```config/param_FCChh.py``` file. Thn you can run with the following command:
```bash
python bin/run.py --FCChh --LHE --send --condor --typelhe mg -p mg_pp_tth01j_5f_50TeV --mg5card mg5/examples/mg_pp_tth01j_5f_50TeV.mg5 -N 1 -n 10000 -q espresso --centos7
```
- Our process is named mg_pp_tth01j_5f_50TeV. This is defined in param_FCChh.py. The process has been added to section  gridpacklist and decaylist of this file.
- We use this mg5 card for LHE generation mg_pp_tth01j_5f_50TeV.mg5. This card is the same as others at different energies. The only change is just the beam energy (25 TeV each)
- We do not use extra model, since the mg5 card already specifed a model loop_sm-no_b_mass. Means Standard Model with loop corrections and no mass for the bottom quark 

This command is succesfully executed on lxplus.

Now we generate more events
## Update database with expert mode for pythia
```bash
python bin/run.py --FCChh --LHE --send --condor --typelhe mg -p mg_pp_tth01j_5f_50TeV --mg5card mg5/examples/mg_pp_tth01j_5f_50TeV.mg5 -N 10 -n 100000 -q espresso --centos7
```

The options ```--ncpus``` and ```--priority``` can also be specified to increase the numbers of cpus on the cluster and to change the priority queue. 


## Update the database of LHE files before running Delphes
===========
Updating the database
==========================

1) First one need to check the eos directories that have been populated with new files. 
Example for LHE:
```
python bin/run.py --FCChh --LHE --checkeos -p mg_pp_tth01j_5f_50TeV [--force]
```
This is successful


2) Second one need to check the quality of the files that have been produced. 
Example for LHE:
```
python bin/run.py --FCChh --LHE --check -p mg_pp_tth01j_5f_50TeV [--force]
```
This is successful


3) Then the checked files needs to be merged:
Example for LHE:
```
python bin/run.py --FCChh --LHE --merge -p mg_pp_tth01j_5f_50TeV [--force]
```

0) To clean jobs that are flagged as bad, the following command can be used for LHE:
```
python bin/run.py --FCChh --LHE --clean --process mg_pp_tth01j_5f_50TeV
```


Cleaning bad jobs
=================
To clean jobs that are flagged as bad, the following command can be used for LHE:
```
python bin/run.py --FCChh --LHE --clean [--process process]
```


Example for Delphes events:
```
python bin/run.py --FCChh --reco --checkeos --prodtag fcc_v04 [--process process] [--force]
```
This is not needed yet
Example for Delphes events:
```
python bin/run.py --FCChh --reco --check --prodtag fcc_v04 [--process process] [--force]
```
Example for Delphes events:
```
python bin/run.py --FCChh --reco --merge --prodtag fcc_v04 [--process process] [--force]
```
and for Delphes
```
python bin/run.py --FCChh --reco --clean --prodtag spring2021 [--process process]
```


As the code checks the files that are in the end written on eos, we need to clean also old jobs that don't produced outputs 3 days after they started.
To do so run the following command for LHE
```
python bin/run.py --FCChh --LHE --cleanold [--process process]
```

and for Delphes
```
python bin/run.py --FCChh --reco --cleanold --prodtag spring2021 [--process process]
```

If you want to completly remove a process, the following command can be used with care for LHE:

```
python bin/run.py --FCChh --LHE --remove --process process 
```

and for Delphes
```
python bin/run.py --FCChh --reco --remove --process process --prodtag spring2021
```

## Generate FCCSW files from the LHE and decay with Pyhtia8
========================================================

1. if you want to let pythia decay without specifiying anything, you can use the default card, but if you have requested extra partons at matrix element, you might need to specify matching parameters to your pythia card
1. if you want to use a specific decay, make sure that the decay you want is in ```decaylist``` and ```branching_ratios``` of the ```param``` (Changed to haa and haaexcl)
1. then create appropriate pythia8 card, by appending standard card with decay syntax if needed and add it to the proper directory.
For FCC-ee this directory is
```
/eos/experiment/fcc/ee/generation/FCC-config/spring2021/FCChh/Generator/Pythia8/
```
**N.B.**: please do not write there directly. Cards should be added by making a PR to https://github.com/HEP-FCC/FCC-config/tree/spring2021.

1. Run jobs:
We need centos7 container to run it
```
python bin/run.py --FCChh --reco --send --type lhep8 --condor -p mg_pp_tth01j_5f_50TeV -N 10 -q espresso --prodtag fcc_v07 --detector II --pycard p8_pp_tth01j_5f.cmd
```
- NUmber of jobs here should be the same as previous LHE jobs
- Here we use the detector card of up-to-date CDR version `FCC v07 II`

Please note that the decay in pythia is optional, and that there is no need to specify the number of events to run on as it will by default run over all the events present in the LHE file

The options ```--ncpus``` and ```--priority``` can also be specified to increase the numbers of cpus on the cluster and to change the priority queue. 

Place where we store samples /eos/home-y/yangc/FCC/DelphesEvents/fcc_v07/II//mgp8_pp_tth01j_5f_50TeV/

### Questions 
1. What is the difference between haaexcl and haa?
2. What jet matching parameter should we use
3. What cuts should we apply at the production of LHE files

