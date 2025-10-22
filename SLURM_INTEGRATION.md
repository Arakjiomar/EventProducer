# SLURM Integration for EventProducer

This document outlines the changes made to integrate SLURM support for Perlmutter supercomputer into the EventProducer framework.

## Overview

The EventProducer has been modified to support SLURM job submission alongside the existing LSF and Condor support. All batch outputs are redirected to the `BatchOutputs` directory in the EventProducer workspace.

## Key Changes

### 1. Main Run Script (`bin/run.py`)

**Added SLURM support:**
- New argument: `--slurm` for SLURM batch submission
- New arguments: `--account` (default: m3792), `--time` (default: 01:00:00)  
- Updated queue choices to include SLURM queues: `debug`, `regular`, `premium`, `shared`, `gpu`, `large`
- Updated all send_* function calls to include SLURM parameters

**SLURM Queue Information:**
- `debug`: 30 minutes, 64 nodes
- `regular`: 12 hours, 3072 nodes (default)
- `premium`: 12 hours, priority access
- `shared`: 12 hours, shared nodes
- `gpu`: 12 hours, GPU nodes
- `large`: 12 hours, >512 nodes

### 2. Utility Functions (`common/utils.py`)

**Added SLURM submission function:**
```python
def SubmitToSlurm(cmd, nbtrials, nsub):
```
- Handles job submission with retry logic
- Extracts job ID from sbatch output
- Returns job status and job ID

### 3. Send Modules (`bin/send_*.py`)

**Updated all send modules to support SLURM:**
- `send_mglhe.py` - MadGraph5 standalone (most relevant for your use case)
- `send_lhe.py` - LHE from gridpacks
- `send_kkmclhe.py` - KKMC jobs
- `send_stdhep.py` - STDHEP jobs
- `send_lhep8.py` - LHE+Pythia8 jobs
- `send_p8.py` - Pythia8 jobs
- `send_fromstdhep.py` - Jobs from STDHEP

**Each module now includes:**
- SLURM parameters in constructor: `isslurm`, `account`, `time`
- SLURM job array support
- SLURM script generation with proper SBATCH directives

### 4. New SLURM Execution Script (`bin/submitMG_slurm.sh`)

**Purpose:** SLURM-specific version of the MadGraph5 execution script

**Key features:**
- Perlmutter environment setup (module load python/3.11, cray-python)
- Configurable MG5 path via `MG5BASE` environment variable
- Standard MG5 workflow: setup → process generation → gridpack creation
- Proper output handling for Perlmutter storage
- Cleanup of temporary directories

**Default Configuration:**
- MG5 installation path: `/global/homes/o/oarakji/software/MG5_aMC_v3_4_2`
- Can be overridden by setting `MG5BASE` environment variable

### 5. Job Configuration for SLURM

**SLURM array jobs created with:**
```bash
#SBATCH --account=m3792
#SBATCH --qos=regular  
#SBATCH --time=01:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --constraint=cpu
#SBATCH --array=1-N  # where N is number of jobs
```

### 6. Directory Structure

**All SLURM outputs go to:**
```
EventProducer/BatchOutputs/FCC/lhe/{process_name}/
├── slurm_job.{JOBID}.out     # Standard output
├── slurm_job.{JOBID}.err     # Standard error  
├── job_params_mglhe.txt      # Job parameters
└── job_desc_mglhe.sh         # SLURM submission script
```

## Usage

### Command Line Changes

**Original command:**
```bash
python bin/run.py --FCChh --LHE --send --condor --typelhe mg -p mg_pp_thj_5f_50TeV --mg5card ./mymg5/mg_pp_thj_5f_50TeV.mg5 -N 1 -n 10 -q microcentury --useV342
```

**New SLURM command:**
```bash
python bin/run.py --FCChh --LHE --send --slurm --typelhe mg -p mg_pp_thj_5f_50TeV --mg5card ./mymg5/mg_pp_thj_5f_50TeV.mg5 -N 1 -n 10 -q regular --account m3792 --time 01:00:00 --useV342
```

### Key Parameter Changes

| Parameter | Condor Default | SLURM Default | Description |
|-----------|----------------|---------------|-------------|
| `--queue` | `workday` | `regular` | Batch queue/QOS |
| `--priority` | `group_u_FCC.local_gen` | `normal` | Job priority |
| `--account` | N/A | `m3792` | SLURM account |
| `--time` | N/A | `01:00:00` | Time limit |

## Setup Requirements

### 1. MadGraph5 Installation

Install MG5 on Perlmutter and set the path:
```bash
export MG5BASE="/path/to/your/MG5_aMC_installation"
```

### 2. Environment Variables

The system will automatically handle environment setup, but you may need to modify:
- Storage paths in parameter files
- MG5 installation path
- Account information

### 3. Storage Configuration

Update storage paths in `config/param_FCChh.py` if needed:
```python
gp_dir = '/path/to/your/gridpack/storage'
lhe_dir = '/path/to/your/lhe/storage'
```

## Error Handling

- **Job retry mechanism**: Up to 10 submission attempts with 10-second delays
- **Unique job IDs**: 9-digit random seeds prevent collisions  
- **Environment isolation**: Uses temporary working directories
- **Error logging**: All outputs captured in BatchOutputs directory

## Monitoring

**Check job status:**
```bash
squeue -u $USER
```

**Check logs:**
```bash
tail -f BatchOutputs/FCC/lhe/{process_name}/slurm_job.{JOBID}.out
```

**Cancel jobs:**
```bash
scancel {JOBID}
```

## Backwards Compatibility

- All existing Condor and LSF functionality preserved
- Existing parameter files compatible
- No changes to output file formats or naming conventions

## Future Enhancements

1. **GPU support**: Add GPU-specific SLURM configurations
2. **Multi-node jobs**: Support for MPI-based parallelization
3. **Automatic resource estimation**: Dynamic CPU/memory/time requests
4. **Job dependency chains**: SLURM job dependency management
