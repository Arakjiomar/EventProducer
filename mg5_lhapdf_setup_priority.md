# Priority Setup: MG5 and LHAPDF on Perlmutter

This is the critical setup needed to run your VBF Higgs MG5 command on Perlmutter.

## Priority 1: MadGraph5 Installation

### Option A: Install MG5 v3.4.2 from Source (Recommended)

```bash
# Navigate to your software directory
cd /global/homes/o/oarakji/

# Download and extract MG5 v3.4.2
wget https://launchpad.net/mg5amcnlo/3.0/3.4.x/+download/MG5_aMC_v3.4.2.tar.gz
tar -xzf MG5_aMC_v3.4.2.tar.gz

# Install required Python dependencies
pip3 install six --user

# Test the installation
cd MG5_aMC_v3_4_2/
./bin/mg5_aMC
# Type 'exit' to quit the interactive session
```

### Option B: Use Existing MG5 Tarball (If Available)

```bash
# If you have the tarball in your current directory
cd /global/homes/o/oarakji/tth_50TeV_studies/
tar -xzf MG5_aMC_v3.4.2.tar.gz -C /global/homes/o/oarakji/

# Test installation
cd /global/homes/o/oarakji/MG5_aMC_v3_4_2/
./bin/mg5_aMC
```

### Update Submit Script

```bash
# Edit the submit script to point to your new MG5 installation
cd /global/homes/o/oarakji/tth_50TeV_studies/EventProducer/
```

---

## Priority 2: LHAPDF Installation and PDF Sets

### Option A: Use Pre-installed LHAPDF (Recommended)

```bash
# Check if LHAPDF is available via module system
module avail lhapdf
# OR try to find it in system paths
which lhapdf-config

# If available, load it
module load lhapdf
# OR use system version directly
```

### Option B: Install LHAPDF (if needed)

```bash
# Create a software directory
mkdir -p /global/homes/o/oarakji/software
cd /global/homes/o/oarakji/software

# Use older Python version or disable Python bindings to avoid Python 3.12 issues
# Download LHAPDF 6.5.4
wget https://lhapdf.hepforge.org/downloads/?f=LHAPDF-6.5.4.tar.gz -O LHAPDF-6.5.4.tar.gz
tar -xzf LHAPDF-6.5.4.tar.gz
cd LHAPDF-6.5.4

# Configure without Python bindings (to avoid Python 3.12 compatibility issues)
./configure --prefix=/global/homes/o/oarakji/software/lhapdf --disable-python
make -j4
make install

# Add to your environment
echo 'export PATH=/global/homes/o/oarakji/software/lhapdf/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/global/homes/o/oarakji/software/lhapdf/lib:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc
```

### Option C: Skip LHAPDF for Now (Quick Test)

```bash
# For immediate MG5 testing, you can skip LHAPDF installation
# MG5 has built-in PDF sets that can be used for testing
echo "Skipping LHAPDF installation for now - using MG5 built-in PDFs"
```

### Download Required PDF Set

```bash
# Create PDF directory
mkdir -p /global/cfs/cdirs/atlas/oarakji/myFiles/lhapdfsets

# Download PDF set 260000 (NNPDF31_nnlo_as_0118) - this is the one your MG5 card uses
cd /global/cfs/cdirs/atlas/oarakji/myFiles/lhapdfsets
wget https://lhapdfsets.web.cern.ch/current/NNPDF31_nnlo_as_0118.tar.gz
tar -xzf NNPDF31_nnlo_as_0118.tar.gz
rm NNPDF31_nnlo_as_0118.tar.gz

# Verify the set
ls -la /global/cfs/cdirs/atlas/oarakji/myFiles/lhapdfsets/NNPDF31_nnlo_as_0118/

# For testing without LHAPDF, create a simple directory structure
# MG5 can work with just the PDF data files
mkdir -p /global/cfs/cdirs/atlas/oarakji/myFiles/lhapdfsets/260000
echo "# Simple PDF info for testing" > /global/cfs/cdirs/atlas/oarakji/myFiles/lhapdfsets/260000/260000.info
```

---

## Priority 3: Update Configuration Files

### Update MG5 Submit Script

```bash
# Edit submitMG_v3_4_2.sh
cd /global/homes/o/oarakji/tth_50TeV_studies/EventProducer/bin/
cp submitMG_v3_4_2.sh submitMG_v3_4_2.sh.backup

# Update the MG5 path
sed -i 's|MG5BASE="/afs/cern.ch/user/o/oarakji/MG5_aMC_v3.4.2-4fhxpu"|MG5BASE="/global/homes/o/oarakji/MG5_aMC_v3_4_2"|g' submitMG_v3_4_2.sh
```

### Update LHAPDF Path in send_lhe.py

```bash
# Edit send_lhe.py
cd /global/homes/o/oarakji/tth_50TeV_studies/EventProducer/bin/
cp send_lhe.py send_lhe.py.backup

# Update LHAPDF path
sed -i 's|export LHAPDF_DATA_PATH=/eos/home-o/oarakji/tth/lhapdfsets/|export LHAPDF_DATA_PATH=/global/cfs/cdirs/atlas/oarakji/myFiles/lhapdfsets/|g' send_lhe.py
```

### Update EOS Test (Quick Fix)

```bash
# Create a mock test file
mkdir -p /global/cfs/cdirs/atlas/oarakji/myFiles/tests/
echo "Mock EOS test file for Perlmutter" > /global/cfs/cdirs/atlas/oarakji/myFiles/tests/testfile.lhe
gzip /global/cfs/cdirs/atlas/oarakji/myFiles/tests/testfile.lhe

# Update config
cd /global/homes/o/oarakji/tth_50TeV_studies/EventProducer/config/
cp param_FCChh.py param_FCChh.py.backup
```

---

## Priority 4: Environment Setup

### Update EventProducer init.sh

First, let's update the EventProducer's init.sh for Perlmutter:

```bash
# Navigate to EventProducer directory
cd /global/homes/o/oarakji/tth_50TeV_studies/EventProducer

# Backup the original init.sh
cp init.sh init.sh.backup

# Create updated init.sh for Perlmutter
cat << 'EOF' > init.sh
# EventProducer environment setup for Perlmutter
# Original Key4HEP setup (commented out for Perlmutter)
#source /cvmfs/sw.hsf.org/key4hep/setup.sh

# Perlmutter doesn't have EOS, so disable or modify
#export EOS_MGM_URL="root://eospublic.cern.ch"

# EventProducer paths
export EVENTPRODUCER=$PWD
export PYTHONPATH=$PWD/..:$PYTHONPATH

# Create log directory
mkdir -p "${EVENTPRODUCER}/log"

echo "EventProducer environment loaded"
echo "EVENTPRODUCER: $EVENTPRODUCER"
EOF
```

### Create Comprehensive Setup Script

```bash
# Create an environment setup script that includes everything
cat << 'EOF' > /global/homes/o/oarakji/setup_mg5_env.sh
#!/bin/bash

# MG5 and LHAPDF environment setup for Perlmutter
export MG5_PATH="/global/homes/o/oarakji/MG5_aMC_v3_4_2"
export PATH="${MG5_PATH}/bin:$PATH"

export LHAPDF_DATA_PATH="/global/cfs/cdirs/atlas/oarakji/myFiles/lhapdfsets"
export PATH="/global/homes/o/oarakji/software/lhapdf/bin:$PATH"
export LD_LIBRARY_PATH="/global/homes/o/oarakji/software/lhapdf/lib:$LD_LIBRARY_PATH"

# EventProducer environment
cd /global/homes/o/oarakji/tth_50TeV_studies/EventProducer
source ./init.sh

# Python environment (if needed)
# module load python
# source activate your_conda_env

echo "=== Environment Summary ==="
echo "MG5 path: $MG5_PATH"
echo "LHAPDF data path: $LHAPDF_DATA_PATH"
echo "EventProducer: $EVENTPRODUCER"
echo "Current directory: $(pwd)"
EOF

chmod +x /global/homes/o/oarakji/setup_mg5_env.sh
```

### Usage Instructions

```bash
# ALWAYS source the complete environment before running EventProducer commands:
source /global/homes/o/oarakji/setup_mg5_env.sh

# This will:
# 1. Set up MG5 paths
# 2. Set up LHAPDF paths  
# 3. Navigate to EventProducer directory
# 4. Source the EventProducer init.sh
# 5. Set EVENTPRODUCER and PYTHONPATH variables
```

---

## Priority 5: Test Installation

### Test MG5

```bash
# Source environment
source /global/homes/o/oarakji/setup_mg5_env.sh

# Test MG5
cd /global/homes/o/oarakji/MG5_aMC_v3_4_2/
./bin/mg5_aMC << EOF
generate p p > h j j
output test_output
exit
EOF

# Check if it worked
ls -la test_output/
```

### Test LHAPDF

```bash
# Test LHAPDF installation
lhapdf-config --help
lhapdf list

# Test PDF set access
python3 -c "
import os
pdf_path = '/global/cfs/cdirs/atlas/oarakji/myFiles/lhapdfsets'
if os.path.exists(f'{pdf_path}/NNPDF31_nnlo_as_0118'):
    print('PDF set found!')
else:
    print('PDF set missing!')
"
```

---

## Quick Verification Checklist

```bash
# Run all these to verify setup
echo "=== Checking MG5 ==="
ls -la /global/homes/o/oarakji/MG5_aMC_v3_4_2/bin/mg5_aMC

echo "=== Checking LHAPDF ==="
ls -la /global/cfs/cdirs/atlas/oarakji/myFiles/lhapdfsets/NNPDF31_nnlo_as_0118/

echo "=== Checking Submit Script ==="
grep "MG5BASE=" /global/homes/o/oarakji/tth_50TeV_studies/EventProducer/bin/submitMG_v3_4_2.sh

echo "=== Checking LHAPDF Path ==="
grep "LHAPDF_DATA_PATH=" /global/homes/o/oarakji/tth_50TeV_studies/EventProducer/bin/send_lhe.py

echo "=== Environment ==="
source /global/homes/o/oarakji/setup_mg5_env.sh
which mg5_aMC
echo $LHAPDF_DATA_PATH
```

---

## After Setup: Test Your Command

Once everything is installed, test your original command:

```bash
# Source environment
source /global/homes/o/oarakji/setup_mg5_env.sh

# Navigate to EventProducer
cd /global/homes/o/oarakji/tth_50TeV_studies/EventProducer

# Test the command (but maybe with fewer events first)
python bin/run.py --FCChh --LHE --send --local --typelhe mg \
  -p mg_pp_vbf_h01j_5f_50TeV \
  --mg5card ./mymg5/mg_pp_vbf_h01j_5f_50TeV.mg5 \
  -N 1 -n 5 --useV342
```

Note: I changed `--condor` to `--local` for initial testing to avoid batch system complications.

---

## Status Checklist

| Task | Command to Check | Status |
|------|------------------|--------|
| MG5 Downloaded | `ls /global/homes/o/oarakji/MG5_aMC_v3_4_2/` | [ ] Done |
| MG5 Working | `/global/homes/o/oarakji/MG5_aMC_v3_4_2/bin/mg5_aMC --help` | [ ] Done |
| LHAPDF Installed | `which lhapdf-config` | [ ] Done |
| PDF Set Downloaded | `ls /global/cfs/cdirs/atlas/oarakji/myFiles/lhapdfsets/` | [ ] Done |
| Submit Script Updated | `grep MG5BASE EventProducer/bin/submitMG_v3_4_2.sh` | [ ] Done |
| LHAPDF Path Updated | `grep LHAPDF_DATA_PATH EventProducer/bin/send_lhe.py` | [ ] Done |
| Environment Script | `source ~/setup_mg5_env.sh` | [ ] Done |
| Test Run | Run test command above | [ ] Done |

---

*Follow this step by step, and you should be able to run MG5 event generation on Perlmutter!*