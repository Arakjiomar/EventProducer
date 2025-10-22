#!/bin/bash

# ----------- 1. Environment Setup -----------
unset LD_LIBRARY_PATH
unset PYTHONHOME
unset PYTHONPATH

# Load environment for Perlmutter
module load python/3.11
module load cray-python

# ----------- 2. Argument Parsing ------------
SCRIPTFILE=${1}
PROCESSNAME=${2}
OUTPUTDIR=${3}
JOBID=${4}
NEVENTS=${5}
CUTFILE=${6:-}
MODELFILE=${7:-}

echo "Starting job with parameters:"
echo "SCRIPTFILE: $SCRIPTFILE"
echo "PROCESSNAME: $PROCESSNAME"
echo "OUTPUTDIR: $OUTPUTDIR"
echo "JOBID: $JOBID"
echo "NEVENTS: $NEVENTS"
echo "CUTFILE: $CUTFILE"
echo "MODELFILE: $MODELFILE"

# ----------- 3. Create Unique Working Directory -----------
WORKDIR=$(mktemp -d /tmp/mg5job_${USER}_${JOBID}_XXXX)
echo "Working directory: $WORKDIR"
cd "$WORKDIR"

# ----------- 4. Diagnostics -----------
echo "python3 location: $(which python3)"
echo "python3 --version: $(python3 --version)"
echo "Current working directory: $(pwd)"

# ----------- 5. Prepare Input Card -----------
cp "$SCRIPTFILE" .
SCRIPT=$(basename "$SCRIPTFILE")
SEED=$((10#$JOBID))
sed -i -e "s/DUMMYSEED/${SEED}/g" -e "s/DUMMYNEVENTS/${NEVENTS}/g" "$SCRIPT"

# Split the MG5 card into config00 and config01, excluding the DELIMITER line
awk '/DELIMITER/{flag=1; next} !flag{print > "config00"} flag{print > "config01"}' "$SCRIPT"

# ----------- 6. Model (UFO) Handling -----------
if [ -n "${MODELFILE:-}" ] && [ -f "${MODELFILE}" ]; then
    echo "Adding model tarball"
    mkdir -p models
    cp "${MODELFILE}" models/
    MODELBASE=$(basename "$MODELFILE")
    cd models
    if [[ $MODELBASE == *.tar.gz ]]; then
        tar -xzf "$MODELBASE"
    elif [[ $MODELBASE == *.tar ]]; then
        tar -xf "$MODELBASE"
    else
        echo "Unknown model file extension: $MODELBASE"
        exit 2
    fi
    cd ..
else
    echo "Model file not specified or not found."
fi

# ----------- 7. Run MadGraph -----------
# Note: Modify this path to point to your MG5 installation on Perlmutter
# You can also set MG5BASE as an environment variable before running
if [ -z "$MG5BASE" ]; then
    MG5BASE="/home/oarakji/tth_50TeV_studies/MG5_aMC_v3_4_2"
fi
MG5EXE="${MG5BASE}/bin/mg5_aMC"

# Check if MG5 exists
if [ ! -f "$MG5EXE" ]; then
    echo "ERROR: MadGraph5 not found at $MG5EXE"
    echo "Please modify the MG5BASE path in submitMG_slurm.sh"
    exit 1
fi

# Create a single MG5 script that includes both process generation and gridpack creation
echo "Creating combined MG5 script..."
cat config00 > combined_mg5_script.mg5
echo "" >> combined_mg5_script.mg5
cat config01 >> combined_mg5_script.mg5

# Run MG5 with the combined script
echo "Running MG5 with combined script..."
$MG5EXE combined_mg5_script.mg5

# ----------- 8. Custom cuts.f -----------
# Find process directory (should be only one created here)
PROC_DIR=$(ls -d */ | grep -E "mg_pp_.*_${SEED}" | head -1)
if [ -z "${PROC_DIR}" ]; then
    echo "Warning: Could not find process directory with seed ${SEED}, trying generic pattern"
    PROC_DIR=$(ls -d */ | grep -m1 -E '[a-zA-Z0-9_]+/$')
fi
echo "Using process directory: ${PROC_DIR}"

if [ -n "${CUTFILE:-}" ] && [ -f "${CUTFILE}" ]; then
    if [ -d "${PROC_DIR}SubProcesses" ]; then
        echo "Adding cuts.f file"
        cp "${CUTFILE}" "${PROC_DIR}SubProcesses/cuts.f"
    else
        echo "Warning: Could not find SubProcesses directory to copy cuts.f"
    fi
else
    echo "cuts.f file not specified, using the default one"
fi

echo "MG5 execution completed with exit code: $?"

# ----------- 9. Locate Output Gridpack -----------
echo "Looking for gridpack in directory: ${PWD}/${PROC_DIR}"
echo "Contents of process directory:"
ls -la "${PWD}/${PROC_DIR}" || echo "Failed to list process directory"

# Look for gridpack tarball in the process directory
GRIDPACK_FILE=$(find "${PWD}/${PROC_DIR}" -name "*gridpack*.tar.gz" -o -name "*gridpack*.tgz" | head -1)
echo "Gridpack search result: ${GRIDPACK_FILE}"

if [ -z "${GRIDPACK_FILE}" ]; then
    echo "ERROR: No gridpack file found!"
    echo "Looking for gridpack files in ${PWD}/${PROC_DIR}:"
    find "${PWD}/${PROC_DIR}" -name "*gridpack*" -o -name "*.tar.gz" -o -name "*.tgz" | head -10
    echo "Full directory tree:"
    find "${PWD}/${PROC_DIR}" -type f | head -20
    exit 3
fi

if [ ! -f "${GRIDPACK_FILE}" ]; then
    echo "ERROR: Gridpack file does not exist: ${GRIDPACK_FILE}"
    exit 4
fi

echo "Found gridpack: ${GRIDPACK_FILE}"

# ----------- 10. Copy Output -----------
# For Perlmutter, modify this to use appropriate storage
# You may need to adapt this section based on your storage setup
OUTDIR="${OUTPUTDIR}/${PROCESSNAME}"
OUTFILE="${OUTDIR}/gridpack_${JOBID}.tar.gz"
echo "Copying gridpack to ${OUTFILE}"
mkdir -p "${OUTDIR}"

# Simple copy for now - modify as needed for your storage system
cp "${GRIDPACK_FILE}" "${OUTFILE}"

# ----------- 11. Cleanup -----------
cd /
rm -rf "$WORKDIR"

echo "Job completed successfully."
