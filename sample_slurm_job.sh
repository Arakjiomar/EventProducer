#!/bin/bash
#SBATCH --job-name=eventproducer_sample
#SBATCH --partition=regular
#SBATCH --account=YOUR_ACCOUNT_NAME  # Replace with your actual SLURM account
#SBATCH --time=02:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4GB
#SBATCH --output=logs/slurm_job.%j.out
#SBATCH --error=logs/slurm_job.%j.err

# ===============================================
# Perlmutter environment and authentication setup
# IMPORTANT: These commands must run before any python commands
# ===============================================

echo "Setting up ATLAS environment..."
source /global/cfs/cdirs/atlas/scripts/setupATLAS.sh

echo "Setting up ATLAS for batch jobs..."
setupATLAS -c el9+batch

echo "Initializing VOMS proxy..."
voms-proxy-init -voms atlas

echo "Sourcing local initialization..."
source ./init.sh

# Check VOMS proxy was created successfully
echo "Checking VOMS proxy..."
voms-proxy-info --exists || {
    echo "ERROR: VOMS proxy creation failed!"
    exit 1
}

echo "VOMS proxy verified successfully."

# ===============================================
# Run EventProducer
# ===============================================

echo "Starting EventProducer job..."
echo "Working directory: $(pwd)"
echo "Running on node: $(hostname)"

# Example EventProducer command for VBF Higgs production
srun python bin/run.py \
    --FCChh \
    --LHE \
    --send \
    --slurm \
    --typelhe mg \
    --process mg_pp_vbf_h01j_5f_50TeV \
    --mg5card ./mymg5/mg_pp_vbf_h01j_5f_50TeV.mg5 \
    --numJobs 1 \
    --numEvents 10 \
    --useV342 \
    --queue regular \
    --account YOUR_ACCOUNT_NAME \
    --time 02:00:00 \
    --nodes 1 \
    --ntasks 1 \
    --cpus-per-task 1 \
    --mem 4GB

echo "EventProducer job completed with exit code: $?"