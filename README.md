EventProducer
=============

This package is used to centrally produced events for FCC-hh at a center of mass of 100 TeV and for FCC-ee. Any other future collider can also be supported by this framework. 

**Perlmutter Adaptation**: This repository has been adapted to work on the NERSC Perlmutter supercomputer with local storage paths. The original CERN EOS/AFS dependencies have been replaced with local NERSC storage directories.

In order to use it, please get in contact with the FCC software and computing coordinators as running this package requires specific rights.


Table of contents
=================
  * [EventProducer](#eventproducer)
  * [Table of contents](#table-of-contents)
  * [Perlmutter Setup](#perlmutter-setup)
  * [Clone and initialisation](#clone-and-initilisation)
  * [Generate LHE events from gridpacks](#generate-lhe-events-from-gridpacks)
  * [Generate LHE files directly from MG5](#generate-lhe-files-directly-from-mg5)
  * [Generate FCCSW files from the LHE and decay with Pyhtia8](#generate-fccsw-files-from-the-lhe-and-decay-with-pyhtia8)
  * [Generate FCCSW files from Pythia8](#generate-fccsw-files-from-pythia8)
  * [Expert mode](#expert-mode)
     * [Updating the database](#updating-the-database)
     * [Cleaning bad jobs](#cleaning-bad-jobs)
     * [Update the webpage](#update-the-webpage)
     * [Create the sample list for analyses](#create-the-sample-list-for-analyses)

Perlmutter Setup
================

This EventProducer has been adapted for the NERSC Perlmutter supercomputer with local storage. Key changes include:

### Environment Setup
Before running any EventProducer commands, you must source the environment setup:
```bash
source /global/homes/o/oarakji/setup_mg5_env.sh
```

This script automatically:
- Sets up MG5 v3.4.2 environment
- Configures LHAPDF paths and PDF sets
- Initializes EventProducer environment
- Sets proper Python paths

### Storage Locations
All data is stored locally on NERSC instead of CERN EOS/AFS:
- **Gridpacks**: `/global/cfs/cdirs/atlas/oarakji/myFiles/gridpacks/`
- **LHE files**: `/global/cfs/cdirs/atlas/oarakji/myFiles/lhe/`
- **ROOT files**: `/global/cfs/cdirs/atlas/oarakji/myFiles/root/`
- **PDF sets**: `/global/homes/o/oarakji/software/lhapdf/share/LHAPDF/`
- **Delphes cards**: `/global/cfs/cdirs/atlas/oarakji/myFiles/delphescards/`
- **Pythia cards**: `/global/cfs/cdirs/atlas/oarakji/myFiles/pythiacards/`

### Example Usage

Before running any EventProducer commands, set up the complete environment:

```bash
# Complete environment setup for Perlmutter
source /global/homes/o/oarakji/setup_complete_env.sh
```

This automatically:
- Activates Python virtual environment with ROOT, numpy, PyYAML, etc.
- Sets up MG5 v3.4.2 and LHAPDF paths
- Configures EventProducer PYTHONPATH
- Sources EventProducer init.sh

**SLURM Execution (Production Ready):**
The EventProducer now includes proper Perlmutter SLURM configuration with all required settings:

```bash
# VBF Higgs generation with SLURM (recommended for production)
python bin/run.py --FCChh --LHE --send --slurm --typelhe mg \
  -p mg_pp_vbf_h01j_5f_50TeV \
  --mg5card ./mymg5/mg_pp_vbf_h01j_5f_50TeV.mg5 \
  -N 1 -n 10 --useV342 \
  --queue debug --account atlas --time 00:30:00
```

**SLURM Features (Automatically Configured):**
- ✅ **CPU Constraint**: Includes `#SBATCH --constraint=cpu` for Perlmutter CPU nodes
- ✅ **Account Specification**: Uses `--account atlas` (required for Perlmutter resource allocation)
- ✅ **Proper Resource Requests**: Single task configuration optimized for MG5 workflows
- ✅ **Environment Setup**: Automatically sources complete Perlmutter environment
- ✅ **Random Seeds**: Uses random job IDs for better statistical independence

**CPU Resource Scaling for Different Workloads:**

The EventProducer uses single CPU by default, but you can optimize resources based on your workload:

*Small/Test Jobs (< 10,000 events):*
```bash
# Default: 1 CPU, 4GB memory, suitable for testing and small gridpacks
python bin/run.py --FCChh --LHE --send --slurm --typelhe mg \
  -p mg_pp_vbf_h01j_5f_50TeV --mg5card ./mymg5/mg_pp_vbf_h01j_5f_50TeV.mg5 \
  -N 1 -n 1000 --useV342 --queue debug --account atlas --time 00:30:00
```

*Medium Jobs (10,000 - 100,000 events):*
```bash
# Recommended: 1 CPU, 8GB memory for standard production
python bin/run.py --FCChh --LHE --send --slurm --typelhe mg \
  -p mg_pp_vbf_h01j_5f_50TeV --mg5card ./mymg5/mg_pp_vbf_h01j_5f_50TeV.mg5 \
  -N 1 -n 50000 --useV342 --queue regular --account atlas --time 02:00:00 \
  --cpus-per-task 1 --mem 8GB
```

*Large Jobs (> 100,000 events or complex processes):*
```bash
# High-memory: 1 CPU, 16GB+ memory for large gridpacks or million-event samples
python bin/run.py --FCChh --LHE --send --slurm --typelhe mg \
  -p mg_pp_complex_process --mg5card ./mymg5/complex_process.mg5 \
  -N 1 -n 1000000 --useV342 --queue regular --account atlas --time 08:00:00 \
  --cpus-per-task 1 --mem 32GB
```

*Multi-job Parallel Strategy (Recommended for large samples):*
```bash
# Split large samples into multiple parallel jobs for better resource utilization
python bin/run.py --FCChh --LHE --send --slurm --typelhe mg \
  -p mg_pp_vbf_h01j_5f_50TeV --mg5card ./mymg5/mg_pp_vbf_h01j_5f_50TeV.mg5 \
  -N 10 -n 100000 --useV342 --queue regular --account atlas --time 04:00:00 \
  --cpus-per-task 1 --mem 8GB
# This creates 10 jobs of 100k events each = 1M total events
```

**Resource Guidelines:**
- **Memory**: ~4GB base + ~0.1MB per 1000 events + gridpack size
- **Time**: ~1-5 minutes per 1000 events (varies by process complexity)  
- **CPU**: MG5 is single-threaded; use multiple jobs rather than multiple CPUs per job
- **Queue Selection**: `debug` (30min max) for testing, `regular` for production

**Available Resource Parameters:**
- `--cpus-per-task N`: Number of CPUs per job (default: 1, recommended: keep at 1)
- `--mem XGB`: Memory allocation (default: 4GB, scale up for large jobs)
- `--time HH:MM:SS`: Job time limit (adjust based on expected runtime)
- `--queue QUEUE`: Partition selection (debug/regular/shared/etc.)

**Troubleshooting:** If SLURM submission fails, check the generated script:
```bash
# Find the generated script and run it directly
bash ./BatchOutputs/FCC/lhe/mg_pp_vbf_h01j_5f_50TeV/slurm_*.sh
```

**Local Execution (Recommended):**
The EventProducer now supports true local execution with the `--local` flag, which bypasses SLURM entirely:

```bash
# Complete VBF Higgs gridpack generation and event production (local)
python bin/run.py --FCChh --LHE --send --condor --typelhe mg \
  -p mg_pp_vbf_h01j_5f_50TeV \
  --mg5card ./mymg5/mg_pp_vbf_h01j_5f_50TeV.mg5 \
  -N 1 -n 10 --useV342 --local
```

**Key Features of Local Execution:**
- ✅ **Gridpack Auto-Management**: Generated gridpacks are automatically moved to `/global/cfs/cdirs/atlas/oarakji/myFiles/gridpacks/` and renamed to match the MG5 card name (e.g., `mg_pp_vbf_h01j_5f_50TeV.tar.gz`)
- ✅ **Random Seeds**: Uses random seeds (100000-999999) instead of sequential numbering for better statistical independence
- ✅ **No SLURM Dependencies**: Runs directly without requiring batch system submission
- ✅ **Complete Workflow**: Handles MG5 process generation, gridpack creation, and file organization in one command

**Direct Script Execution (Advanced):**
```bash
# Direct script execution for debugging
bin/submitMG_v3_4_2.sh \
  $(pwd)/mymg5/mg_pp_vbf_h01j_5f_50TeV.mg5 \
  mg_pp_vbf_h01j_5f_50TeV \
  /global/cfs/cdirs/atlas/oarakji/myFiles/lhe \
  12345 10 \
  $(pwd)/cuts.f $(pwd)/model.tgz
```

Clone and initialisation
========================

This EventProducer has been adapted for Perlmutter and is ready to use. If you need to clone it:
```bash
git clone git@github.com:HEP-FCC/EventProducer.git
```

To initialize the environment for Perlmutter:
```bash
# First, source the global environment setup
source /global/homes/o/oarakji/setup_mg5_env.sh

# Then initialize EventProducer (done automatically by setup script above)
# source ./init.sh
```

<<<<<<< HEAD
The environment setup script handles all necessary configuration for MG5, LHAPDF, and EventProducer.
=======
Then initialise:
```
source /global/cfs/cdirs/atlas/scripts/setupATLAS.sh
setupATLAS -c el9+batch
source ./init.sh
```
>>>>>>> origin/perlmutter-version


Generate LHE files from gridpacks
=================================

To send jobs starting from a gridpack that does not exist but that you have produced, do the following:

1. Place gridpack in the local Perlmutter storage:
   * For FCC-hh: `/global/cfs/cdirs/atlas/oarakji/myFiles/gridpacks/`
   * For FCC-ee: `/global/cfs/cdirs/atlas/oarakji/myFiles/gridpacks/`

2. Name the gridpack appropriately:
   * If from Madgraph: `mg_process` (use `gp_mg` option when running)
   * If from POWHEG: `pw_process` (use `gp_pw` option when running)

3. Add entry to `config/param_FCCee.py` or `config/param_FCChh.py` in the `gridpacklist` list

If the gridpack already exists or has been properly added to the config, then run:

```bash
python bin/run.py --FCCee --LHE --send --local --typelhe <gp> -p <process> -n <nevents> -N <njobs> --prodtag <prodtag> --detector <detector>
```

Example for local execution (10 jobs of 10,000 events):

```bash
# Source environment first
source /global/homes/o/oarakji/setup_mg5_env.sh

# Run generation
python bin/run.py --FCCee --LHE --send --local --typelhe gp_mg -p mg_ee_zhh_ecm365 -n 10000 -N 10 --prodtag spring2021 --detector IDEA
```

Note: Replace `--condor` with `--local` for local execution on Perlmutter. 


Generate LHE files directly from MG5
=====================================

To send jobs directly from MG5, you need a configuration file (see examples in `mymg5` directory `*.mg5`) and optionally:

* A `cuts.f` file (containing additional cuts)
* A model (see in `models` directory for instance)

**N.B.** Examples for both FCC-ee and FCC-hh are available in the `mymg5` directory.

You need to add the process to the `config/param_FCChh.py` or `config/param_FCCee.py` file. Then you can run:

```bash
# Source environment first
source /global/homes/o/oarakji/setup_mg5_env.sh

# Run MG5 generation example (VBF Higgs at 50 TeV)
python bin/run.py --FCChh --LHE --send --local --typelhe mg \
  -p mg_pp_vbf_h01j_5f_50TeV \
  --mg5card ./mymg5/mg_pp_vbf_h01j_5f_50TeV.mg5 \
  -N 2 -n 10000 --useV342
```

Note: Replace `--condor` with `--local` for local execution on Perlmutter, and remove queue options as they are not needed for local execution. 


Improved Gridpack Management (New Features)
===========================================

The EventProducer has been enhanced with automatic gridpack management for streamlined workflow:

### Automatic Gridpack Organization
When using local execution (`--local` flag), the system automatically:

1. **Generates**: Creates gridpack during MG5 process execution
2. **Locates**: Finds the generated gridpack in the MG5 output directory
3. **Moves**: Transfers gridpack to the centralized storage location: `/global/cfs/cdirs/atlas/oarakji/myFiles/gridpacks/`
4. **Renames**: Uses the MG5 card filename as the gridpack name (e.g., `mg_pp_vbf_h01j_5f_50TeV.mg5` → `mg_pp_vbf_h01j_5f_50TeV.tar.gz`)

### Benefits
- **Consistent Naming**: Gridpack names directly match the MG5 card names for easy identification
- **Centralized Storage**: All gridpacks in one location for easy access and management  
- **No Manual Steps**: Complete automation from generation to final storage
- **Random Seeds**: Uses random seeds (100000-999999) for better statistical independence

### Example Usage
```bash
# Complete workflow: generates process, creates gridpack, and organizes files
python bin/run.py --FCChh --LHE --send --condor --typelhe mg \
  -p mg_pp_vbf_h01j_5f_50TeV \
  --mg5card ./mymg5/mg_pp_vbf_h01j_5f_50TeV.mg5 \
  -N 1 -n 10 --useV342 --local

# Result: gridpack automatically saved as:
# /global/cfs/cdirs/atlas/oarakji/myFiles/gridpacks/mg_pp_vbf_h01j_5f_50TeV.tar.gz
```

Gridpack vs Event Generation Commands
====================================

The EventProducer supports two main workflows for physics event generation:

## 1. Gridpack Generation (First Step)

Gridpack generation creates a compressed archive containing all the matrix element information needed to generate events later. This is typically done once per process and can be reused multiple times for event generation.

### Key Characteristics:
- **Output**: Produces gridpack files (`*.tar.gz`) in `/global/cfs/cdirs/atlas/oarakji/myFiles/output_mg5/` 
- **Reusable**: One gridpack can generate multiple event samples with different parameters
- **Time**: Takes longer initially but enables fast event generation later
- **Storage**: Compact gridpack files (typically 10-100 MB)

### Command Structure for Gridpack Generation:
```bash
# Setup environment
source /global/homes/o/oarakji/setup_complete_env.sh

# Generate gridpack using MG5 (no LHE events yet)
python bin/run.py --FCChh --LHE --send --slurm --typelhe mg \
  -p <process_name> \
  --mg5card ./mymg5/<process_card>.mg5 \
  -N 1 -n 0 --useV342 \
  --queue debug --account atlas --time 00:30:00
```

### Example - VBF Higgs Gridpack Generation:
```bash
python bin/run.py --FCChh --LHE --send --slurm --typelhe mg \
  -p mg_pp_vbf_h01j_5f_50TeV \
  --mg5card ./mymg5/mg_pp_vbf_h01j_5f_50TeV.mg5 \
  -N 1 -n 0 --useV342 \
  --queue debug --account atlas --time 00:30:00
```

**Important Notes for Gridpack Generation:**
- **MUST include `--LHE` flag** - this is required even for gridpack-only generation
- Use `-n 0` to generate only the gridpack without events
- Use `-N 1` since you only need one gridpack per process
- The MG5 card output path determines where the gridpack is stored
- All `.mg5` cards now output to `/global/cfs/cdirs/atlas/oarakji/myFiles/output_mg5/`

## 2. Event Generation (Second Step)

Event generation uses existing gridpacks to produce LHE event files. This step is fast and can be parallelized across many jobs.

### Key Characteristics:
- **Input**: Uses existing gridpack files
- **Output**: Produces LHE event files in `/global/cfs/cdirs/atlas/oarakji/myFiles/lhe/`
- **Scalable**: Can run many parallel jobs to generate large event samples
- **Time**: Fast execution (minutes to hours depending on event count)
- **Storage**: Large LHE files (can be GBs for high statistics)

### Command Structure for Event Generation:
```bash
# Setup environment
source /global/homes/o/oarakji/setup_complete_env.sh

# Generate LHE events from existing gridpack
python bin/run.py --FCChh --LHE --send --slurm --typelhe gp_mg \
  -p <process_name> \
  -N <num_jobs> -n <events_per_job> \
  --queue regular --account atlas --time 02:00:00
```

### Example - Generate 100k VBF Higgs Events (10 jobs × 10k events):
```bash
python bin/run.py --FCChh --LHE --send --slurm --typelhe gp_mg \
  -p mg_pp_vbf_h01j_5f_50TeV \
  -N 10 -n 10000 \
  --queue regular --account atlas --time 02:00:00
```

## 3. Combined Generation (Single Step)

You can also generate both gridpack and events in a single command:

```bash
# Generate gridpack AND events in one go
python bin/run.py --FCChh --LHE --send --slurm --typelhe mg \
  -p mg_pp_vbf_h01j_5f_50TeV \
  --mg5card ./mymg5/mg_pp_vbf_h01j_5f_50TeV.mg5 \
  -N 5 -n 10000 --useV342 \
  --queue regular --account atlas --time 04:00:00
```

## Command Comparison Table

| Purpose | `--typelhe` | `-N` (jobs) | `-n` (events) | `--mg5card` | Output |
|---------|-------------|-------------|---------------|-------------|---------|
| **Gridpack Only** | `mg` | 1 | 0 | Required | Gridpack files |
| **Events from Gridpack** | `gp_mg` | Many | Many | Not used | LHE files |
| **Both Together** | `mg` | Many | Many | Required | Both |

## Workflow Recommendations

### For Production (Recommended):
1. **Step 1**: Generate gridpack once
2. **Step 2**: Generate events from gridpack (can repeat with different parameters)

### For Testing:
- Use combined generation with small numbers (`-N 1 -n 100`)

### Storage Locations:
- **Gridpacks**: `/global/cfs/cdirs/atlas/oarakji/myFiles/output_mg5/<process>/`
- **LHE Events**: `/global/cfs/cdirs/atlas/oarakji/myFiles/lhe/<process>/`
- **Batch Logs**: `./BatchOutputs/FCC/lhe/<process>/`


Generate FCCSW files from the LHE and decay with Pythia8
========================================================

1. If you want to let Pythia decay without specifying anything, you can use the default card, but if you have requested extra partons at matrix element, you might need to specify matching parameters to your Pythia card
2. If you want to use a specific decay, make sure that the decay you want is in `decaylist` and `branching_ratios` of the `param`
3. Create appropriate Pythia8 card and place it in the local Pythia cards directory:

```
/global/cfs/cdirs/atlas/oarakji/myFiles/pythiacards/
```

4. Run jobs:

```bash
# Source environment first
source /global/homes/o/oarakji/setup_mg5_env.sh

# Run Pythia8 processing
python bin/run.py --FCChh --reco --send --type lhep8 --local \
  -p <process> -N <njobs> --prodtag <prodtag> --detector <detector>
```

Example to produce 10 jobs of FCC Delphes events:

```bash
python bin/run.py --FCCee --reco --send --type lhep8 --local \
  -p mg_ee_zhh_ecm365 -N 10 --prodtag spring2021 --detector IDEA
```

Please note that the decay in Pythia is optional, and there is no need to specify the number of events to run on as it will by default run over all the events present in the LHE file. 


Generate FCCSW files from Pythia8
=================================

The Pythia8 manual is available here: http://home.thep.lu.se/~torbjorn/pythia81html/Welcome.html

1. Define process in `pythialist` in the `param` corresponding to your job flavour
2. Write Pythia8 process card and put it in: `/global/cfs/cdirs/atlas/oarakji/myFiles/pythiacards/`
   For example: `p8_ee_Zbb_ecm91.cmd`

3. Send jobs:

```bash
# Source environment first
source /global/homes/o/oarakji/setup_mg5_env.sh

# Run Pythia8 generation
python bin/run.py --FCChh --reco --send --type p8 --local \
  -p <process> --pycard <pythia_card> -n <nevents> -N <njobs> \
  --prodtag <prodtag> --detector <detector>
```

Example to produce 1 job of 10,000 events of ZH at FCC-ee 240GeV:

```bash
python bin/run.py --FCCee --reco --send --type p8 --local \
  -p p8_ee_ZH_ecm240 -n 10000 -N 1 --prodtag spring2021 --detector IDEA
```

**Important**: If `--pycard` option not specified, this step will run with the default Pythia8 card (in this case `p8_ee_default.cmd`), that does not include specific decays nor specific matching/merging parameters. 


Expert mode
===========

The following commands should be run with care, as they update the database, webpage etc...
They would typically run every two hours with crontab on the original CERN system, but on Perlmutter they should be run manually as needed.
The `--force` option is used to force the script to run; to optimize running time, processes that have not been flagged will not be checked.

Note: All references to EOS have been replaced with local Perlmutter storage paths. Database and web functionality may need adaptation for the Perlmutter environment.

Updating the database
=====================

1) First check the local directories that have been populated with new files:

Example for LHE:
```bash
python bin/run.py --FCCee --LHE --checklocal [--process process] [--force]
```

Example for Delphes events:
```bash
python bin/run.py --FCCee --reco --checklocal --prodtag fcc_v04 [--process process] [--force]
```

2) Second check the quality of the files that have been produced:

Example for LHE:
```bash
python bin/run.py --FCCee --LHE --check [--process process] [--force]
```

Example for Delphes events:
```bash
python bin/run.py --FCCee --reco --check --prodtag fcc_v04 [--process process] [--force]
```

3) Then the checked files need to be merged:

Example for LHE:
```bash
python bin/run.py --FCCee --LHE --merge [--process process] [--force]
```

Example for Delphes events:
```bash
python bin/run.py --FCCee --reco --merge --prodtag fcc_v04 [--process process] [--force]
```

Cleaning bad jobs
=================

To clean jobs that are flagged as bad, the following command can be used for LHE:

```bash
python bin/run.py --FCCee --LHE --clean [--process process]
```

and for Delphes:

```bash
python bin/run.py --FCCee --reco --clean --prodtag spring2021 [--process process]
```

As the code checks the files that are written to local storage, we need to clean also old jobs that don't produce outputs 3 days after they started.
To do so run the following command for LHE:

```bash
python bin/run.py --FCCee --LHE --cleanold [--process process]
```

and for Delphes:

```bash
python bin/run.py --FCCee --reco --cleanold --prodtag spring2021 [--process process]
```

If you want to completely remove a process, the following command can be used with care for LHE:

```bash
python bin/run.py --FCCee --LHE --remove --process process 
```

and for Delphes:

```bash
python bin/run.py --FCCee --reco --remove --process process --prodtag spring2021
```


Update the webpage
==================

The webpage can be updated after the files have been checked and merged by running for LHE:

```bash
python bin/run.py --FCCee --LHE --web
```

and for Delphes:

```bash
python bin/run.py --FCCee --reco --web --prodtag spring2021
```


Create the sample list for analyses
===================================

To create the list of samples to be used in physics analyses:

```bash
python bin/run.py --FCCee --reco --sample --prodtag spring2021
```


Perlmutter Adaptation Notes
===========================

This EventProducer has been fully adapted for the NERSC Perlmutter environment:

* **Storage**: All EOS/AFS references replaced with local NERSC storage at `/global/cfs/cdirs/atlas/oarakji/myFiles/`
* **Software**: MG5 v3.4.2 and LHAPDF 6.5.4 installed locally with proper environment setup
* **Execution**: Use `--local` instead of `--condor` for job submission
* **Environment**: Source `/global/homes/o/oarakji/setup_mg5_env.sh` before running any commands
* **Web functionality**: May require additional setup for Perlmutter environment
* **Database operations**: Adapted to work with local file system instead of EOS
