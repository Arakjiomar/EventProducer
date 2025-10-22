#!/bin/bash

# ----------- 1. Environment Setup for Perlmutter -----------
# Use our custom Perlmutter environment setup
echo "Setting up Perlmutter environment..."

# Activate the Python virtual environment that has all the required packages
source /global/u2/o/oarakji/tth_50TeV_studies/.venv/bin/activate

# Set PYTHONPATH for EventProducer
export PYTHONPATH=/global/homes/o/oarakji/tth_50TeV_studies:$PYTHONPATH

# Set MG5 environment
export MG5BASE="/global/homes/o/oarakji/MG5_aMC_v3_4_2"
export PATH="${MG5BASE}/bin:$PATH"

# Set LHAPDF environment
export LHAPDF_DATA_PATH="/global/homes/o/oarakji/software/lhapdf/share/LHAPDF"
export PATH="/global/homes/o/oarakji/software/lhapdf/bin:$PATH"
export LD_LIBRARY_PATH="/global/homes/o/oarakji/software/lhapdf/lib:$LD_LIBRARY_PATH"

# ----------- 2. Argument Parsing ------------
SCRIPTFILE=${1}
PROCESSNAME=${2}
OUTPUTDIR=${3}
JOBID=${4}
NEVENTS=${5}
CUTFILE=${6:-}
MODELFILE=${7:-}

# ----------- 3. Create Unique Working Directory -----------
WORKDIR=$(mktemp -d /tmp/mg5job_${USER}_${JOBID}_XXXX)
echo "Working directory: $WORKDIR"
cd "$WORKDIR"

# ----------- 4. f2py Symlink Workaround -----------
mkdir -p "$PWD/f2py_bin"
# Use f2py from our virtual environment
ln -sf "$(which f2py)" "$PWD/f2py_bin/f2py3.11"
export PATH="$PWD/f2py_bin:$PATH"

# ----------- 5. Diagnostics -----------
echo "python3 location: $(which python3)"
echo "python3 --version: $(python3 --version)"
echo "numpy version: $(python3 -c 'import numpy; print(numpy.__version__)')"
echo "f2py3.11 location: $(which f2py3.11)"
head -5 $(which f2py3.11)

# ----------- 6. Prepare Input Card -----------
cp "$SCRIPTFILE" .
SCRIPT=$(basename "$SCRIPTFILE")
SEED=$((10#$JOBID))
sed -i -e "s/DUMMYSEED/${SEED}/g" -e "s/DUMMYNEVENTS/${NEVENTS}/g" "$SCRIPT"

# Split the MG5 card into config00 and config01, excluding the DELIMITER line
awk '/DELIMITER/{flag=1; next} !flag{print > "config00"} flag{print > "config01"}' "$SCRIPT"

# ----------- 7. Model (UFO) Handling -----------
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

# ----------- 8. Run MadGraph (using your install) -----------
MG5BASE="/global/homes/o/oarakji/MG5_aMC_v3_4_2"
MG5EXE="${MG5BASE}/bin/mg5_aMC"

# Create a single MG5 script that includes both process generation and gridpack creation
echo "Creating combined MG5 script..."
cat config00 > combined_mg5_script.mg5
echo "" >> combined_mg5_script.mg5
cat config01 >> combined_mg5_script.mg5

# Run MG5 with the combined script
echo "Running MG5 with combined script..."
$MG5EXE combined_mg5_script.mg5

# ----------- 9. Custom cuts.f -----------
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

# ----------- 10. Locate Output Gridpack -----------
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

# ----------- 11. Copy Output to Local Storage -----------
# Automatically determine gridpack directory from config
# Extract the base directory from the script path to find the config
SCRIPT_DIR=$(dirname "${SCRIPTFILE}")
BASE_DIR=$(dirname "${SCRIPT_DIR}")

# Try to find and read the gridpack directory from config
if [ -f "${BASE_DIR}/config/param_FCChh.py" ]; then
    GP_DIR=$(python3 -c "
import sys
sys.path.insert(0, '${BASE_DIR}')
try:
    from config.param_FCChh import gp_dir
    print(gp_dir.rstrip('/'))
except:
    print('/global/cfs/cdirs/atlas/oarakji/myFiles/gridpacks')
")
elif [ -f "${BASE_DIR}/config/param_FCCee.py" ]; then
    GP_DIR=$(python3 -c "
import sys
sys.path.insert(0, '${BASE_DIR}')
try:
    from config.param_FCCee import gp_dir
    print(gp_dir.rstrip('/'))
except:
    print('/global/cfs/cdirs/atlas/oarakji/myFiles/gridpacks')
")
else
    # Fallback to the default Perlmutter gridpack directory
    GP_DIR="/global/cfs/cdirs/atlas/oarakji/myFiles/gridpacks"
    echo "Warning: No config file found, using default Perlmutter gridpack directory"
fi

OUTDIR="${GP_DIR}/${PROCESSNAME}"
OUTFILE="${OUTDIR}/gridpack_${JOBID}.tar.gz"
echo "Copying gridpack to ${OUTFILE}"
mkdir -p "${OUTDIR}"
# Use regular cp instead of xrdcp for local filesystem
cp "${GRIDPACK_FILE}" "${OUTFILE}"

# ----------- 12. Cleanup -----------
cd /
rm -rf "$WORKDIR"

echo "Job completed successfully."