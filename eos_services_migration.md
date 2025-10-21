# EOS Services Migration to Perlmutter

This document covers how to handle the remaining EOS-dependent services and files that are referenced in `param_FCChh.py` but not yet migrated to Perlmutter.

## Services to Handle

### 1. EOS Test File
- **Current Path**: `/eos/experiment/fcc/hh/tests/testfile.lhe.gz`
- **Purpose**: Used to test EOS connectivity and file access
- **Size**: 1,312,594 bytes (1.3 MB)

### 2. LHE Web Output
- **Current Path**: `/eos/experiment/fcc/www/data/FCChh/LHEevents.txt`
- **Purpose**: Web interface for LHE event statistics

### 3. Delphes Web Output
- **Current Path**: `/eos/experiment/fcc/www/data/FCChh/Delphesevents_VERSION_DETECTOR.txt`
- **Purpose**: Web interface for Delphes event statistics

---

## Migration Options

### Option 1: Download Test File (Recommended)

```bash
# On lxplus, copy the test file
scp /eos/experiment/fcc/hh/tests/testfile.lhe.gz oarakji@perlmutter.nersc.gov:/global/cfs/cdirs/atlas/oarakji/myFiles/

# Create a tests directory structure
mkdir -p /global/cfs/cdirs/atlas/oarakji/myFiles/tests/
mv /global/cfs/cdirs/atlas/oarakji/myFiles/testfile.lhe.gz /global/cfs/cdirs/atlas/oarakji/myFiles/tests/
```

**Then update param_FCChh.py:**
```python
# eos tests
eostest = '/global/cfs/cdirs/atlas/oarakji/myFiles/tests/testfile.lhe.gz'
eostest_size = 1312594
```

### Option 2: Create Mock Test File

```bash
# Create tests directory
mkdir -p /global/cfs/cdirs/atlas/oarakji/myFiles/tests/

# Create a dummy LHE file for testing (if you can't access the original)
cd /global/cfs/cdirs/atlas/oarakji/myFiles/tests/
cat << 'EOF' > testfile.lhe
<LesHouchesEvents version="1.0">
<header>
Mock test file for EOS connectivity testing
</header>
<init>
1 1 1.0 1.0 1.0 1.0 1 1 1 1
</init>
<event>
1 1 1.0 1.0 1.0 1.0
</event>
</LesHouchesEvents>
EOF

# Compress it
gzip testfile.lhe
```

**Then update param_FCChh.py:**
```python
# eos tests  
eostest = '/global/cfs/cdirs/atlas/oarakji/myFiles/tests/testfile.lhe.gz'
eostest_size = $(stat -c%s /global/cfs/cdirs/atlas/oarakji/myFiles/tests/testfile.lhe.gz)
```

### Option 3: Disable EOS Testing (Quick Fix)

**Update param_FCChh.py:**
```python
# eos tests - DISABLED for Perlmutter
eostest = None  # '/eos/experiment/fcc/hh/tests/testfile.lhe.gz'
eostest_size = 0  # 1312594
```

**And modify the utils.py file** to skip EOS testing:
```python
# In EventProducer/common/utils.py, find the testeos function and modify it:
def testeos(eostest, eostest_size):
    if eostest is None:
        print("INFO: EOS testing disabled for Perlmutter")
        return True
    # ... rest of function
```

---

## Web Services Migration

### Option 1: Create Local Web Directory Structure

```bash
# Create web output directories
mkdir -p /global/cfs/cdirs/atlas/oarakji/myFiles/www/data/FCChh/

# Create placeholder files
touch /global/cfs/cdirs/atlas/oarakji/myFiles/www/data/FCChh/LHEevents.txt
touch /global/cfs/cdirs/atlas/oarakji/myFiles/www/data/FCChh/Delphesevents_VERSION_DETECTOR.txt
```

**Update param_FCChh.py:**
```python
# web
lhe_web = "/global/cfs/cdirs/atlas/oarakji/myFiles/www/data/FCChh/LHEevents.txt"
delphes_web = "/global/cfs/cdirs/atlas/oarakji/myFiles/www/data/FCChh/Delphesevents_VERSION_DETECTOR.txt"
```

### Option 2: Disable Web Output (Recommended for Testing)

**Update param_FCChh.py:**
```python
# web - DISABLED for Perlmutter
lhe_web = None  # "/eos/experiment/fcc/www/data/FCChh/LHEevents.txt"
delphes_web = None  # "/eos/experiment/fcc/www/data/FCChh/Delphesevents_VERSION_DETECTOR.txt"
```

**And modify the printer.py file** to handle None paths:
```python
# In EventProducer/common/printer.py, add checks for None paths
if lhe_web is None or delphes_web is None:
    print("INFO: Web output disabled for Perlmutter")
    return
```

---

## Recommended Quick Setup

For immediate testing, use this approach:

### 1. Create Mock Test File

```bash
mkdir -p /global/cfs/cdirs/atlas/oarakji/myFiles/tests/
echo "Mock EOS test file" > /global/cfs/cdirs/atlas/oarakji/myFiles/tests/testfile.lhe
gzip /global/cfs/cdirs/atlas/oarakji/myFiles/tests/testfile.lhe
```

### 2. Update param_FCChh.py

```python
# eos tests
eostest = '/global/cfs/cdirs/atlas/oarakji/myFiles/tests/testfile.lhe.gz'
eostest_size = 38  # Size of your mock file

# web - disabled for Perlmutter
lhe_web = "/global/cfs/cdirs/atlas/oarakji/myFiles/www/data/FCChh/LHEevents.txt"
delphes_web = "/global/cfs/cdirs/atlas/oarakji/myFiles/www/data/FCChh/Delphesevents_VERSION_DETECTOR.txt"
```

### 3. Create Web Directories

```bash
mkdir -p /global/cfs/cdirs/atlas/oarakji/myFiles/www/data/FCChh/
touch /global/cfs/cdirs/atlas/oarakji/myFiles/www/data/FCChh/LHEevents.txt
touch /global/cfs/cdirs/atlas/oarakji/myFiles/www/data/FCChh/Delphesevents_VERSION_DETECTOR.txt
```

---

## Verification Commands

After making changes, verify your setup:

```bash
# Check all directories exist
ls -la /global/cfs/cdirs/atlas/oarakji/myFiles/tests/
ls -la /global/cfs/cdirs/atlas/oarakji/myFiles/www/data/FCChh/

# Test file sizes
stat /global/cfs/cdirs/atlas/oarakji/myFiles/tests/testfile.lhe.gz

# Test your EventProducer config
cd /global/homes/o/oarakji/tth_50TeV_studies/EventProducer
python3 -c "
import config.param_FCChh as para
print('EOS test file:', para.eostest)
print('LHE web:', para.lhe_web)
print('Delphes web:', para.delphes_web)
"
```

---

## Status Checklist

| Item | Action | Status |
|------|--------|--------|
| EOS test file | [ ] Download original [ ] Create mock [ ] Disable | [ ] Done |
| LHE web output | [ ] Create local dir [ ] Disable | [ ] Done |
| Delphes web output | [ ] Create local dir [ ] Disable | [ ] Done |
| Update param_FCChh.py | [ ] Update paths | [ ] Done |
| Test configuration | [ ] Verify paths work | [ ] Done |

---

*Choose the approach that best fits your immediate needs. For production use, consider setting up proper web services on Perlmutter if needed.*