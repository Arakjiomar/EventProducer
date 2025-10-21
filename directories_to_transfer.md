
```
# CERN to NERSC Migration: Reference Directory Checklist

This document lists all non-bulk, supporting directories and files to migrate from `/afs` or `/eos` on lxplus (CERN) to your NERSC project directory `/global/cfs/cdirs/atlas/oarakji/myFiles/`.

## To Transfer

### 1. Delphes Cards
- **Source (lxplus):**
  ```
  /eos/experiment/fcc/hh/utils/delphescards/
  ```
- **NERSC Destination:**
  ```
  /global/cfs/cdirs/atlas/oarakji/myFiles/delphescards/
  ```

---

### 2. Pythia Cards
- **Source (lxplus):**
  ```
  /eos/experiment/fcc/hh/utils/pythiacards/
  ```
- **NERSC Destination:**
  ```
  /global/cfs/cdirs/atlas/oarakji/myFiles/pythiacards/
  ```

---

### 3. Process Dictionaries (JSON)
- **Source (lxplus):**
  ```
  /eos/experiment/fcc/www/data/FCCDicts/FCChh_procDict_VERSION_DETECTOR.json
  ```
- **NERSC Destination:**
  ```
  /global/cfs/cdirs/atlas/oarakji/myFiles/FCCDicts/FCChh_procDict_VERSION_DETECTOR.json
  ```

---

### 4. YAML Directory
- **Source (lxplus):**
  ```
  /eos/home-o/oarakji/tth/yaml/FCChh/
  ```
- **NERSC Destination:**
  ```
  /global/cfs/cdirs/atlas/oarakji/myFiles/yaml/FCChh/
  ```

---

### 5. Config Directory and Scripts
- **Source (lxplus):**
  ```
  /eos/experiment/fcc/hh/utils/config/
  ```
- **NERSC Destination:**
  ```
  /global/cfs/cdirs/atlas/oarakji/myFiles/config/
  ```

---

### 6. Other Referenced Files (add as needed)
- **Examples:**  
  Any other small supporting files, scripts, or parameter/config files you reference in your scripts.

---

## Not Transferring (Typically Skipped):

- **Bulk LHE files** (`/eos/home-o/oarakji/tth/lhe/`)
- **Bulk ROOT files** (`/eos/home-o/oarakji/tth/myRoot/`)
- **Gridpacks** (`/eos/home-o/oarakji/tth/gridpacks/`)
  
(Transfer only if you need to process/analyze these data files on Perlmutter.)

---

## Example Transfer Commands

### Option 1: Transfer directories individually (recommended for troubleshooting)

```bash
# Create separate archives for each directory
tar czvf delphescards.tgz /eos/experiment/fcc/hh/utils/delphescards/
tar czvf pythiacards.tgz /eos/experiment/fcc/hh/utils/pythiacards/
tar czvf FCCDicts.tgz /eos/experiment/fcc/www/data/FCCDicts/
tar czvf config.tgz /eos/experiment/fcc/hh/utils/config/

# For YAML directory, handle potential permission issues
tar czvf yaml_FCChh.tgz /eos/home-o/oarakji/tth/yaml/FCChh/ --warning=no-file-changed --ignore-failed-read
```

### Option 2: Transfer all at once (if no permission issues)

```bash
tar czvf eventproducer_support.tgz \
    /eos/experiment/fcc/hh/utils/delphescards/ \
    /eos/experiment/fcc/hh/utils/pythiacards/ \
    /eos/experiment/fcc/www/data/FCCDicts/ \
    /eos/experiment/fcc/hh/utils/config/ \
    /eos/home-o/oarakji/tth/yaml/FCChh/ \
    --warning=no-file-changed --ignore-failed-read
```

### Option 3: Use rsync for selective transfer (recommended for large directories)

```bash
# Sync only specific file types or exclude problematic files
rsync -avz --progress /eos/home-o/oarakji/tth/yaml/FCChh/ ./yaml_backup/ \
    --include="*.yaml" --include="*/" --exclude="*"
tar czvf yaml_FCChh.tgz ./yaml_backup/
```

### Transfer to NERSC and extract:

#### If using individual archives:

```bash
# Transfer each archive
scp delphescards.tgz oarakji@perlmutter.nersc.gov:/global/cfs/cdirs/atlas/oarakji/myFiles/
scp pythiacards.tgz oarakji@perlmutter.nersc.gov:/global/cfs/cdirs/atlas/oarakji/myFiles/
scp FCCDicts.tgz oarakji@perlmutter.nersc.gov:/global/cfs/cdirs/atlas/oarakji/myFiles/
scp config.tgz oarakji@perlmutter.nersc.gov:/global/cfs/cdirs/atlas/oarakji/myFiles/
scp yaml_FCChh.tgz oarakji@perlmutter.nersc.gov:/global/cfs/cdirs/atlas/oarakji/myFiles/

# On NERSC, extract each archive (preserving directory structure)
cd /global/cfs/cdirs/atlas/oarakji/myFiles/
tar xzvf delphescards.tgz --transform='s|.*/utils/|./|'        # Creates ./delphescards/
tar xzvf pythiacards.tgz --transform='s|.*/utils/|./|'         # Creates ./pythiacards/  
tar xzvf FCCDicts.tgz --transform='s|.*/data/|./|'             # Creates ./FCCDicts/
tar xzvf config.tgz --transform='s|.*/utils/|./|'              # Creates ./config/
tar xzvf yaml_FCChh.tgz --transform='s|.*/tth/|./|'            # Creates ./yaml/FCChh/
```

#### If using single archive:

```bash
scp eventproducer_support.tgz oarakji@perlmutter.nersc.gov:/global/cfs/cdirs/atlas/oarakji/myFiles/
cd /global/cfs/cdirs/atlas/oarakji/myFiles/
tar xzvf eventproducer_support.tgz --strip-components=4
```

---

## Status Checklist

| Item               | CERN Source Location                                         | NERSC Target Location                                                | Status                                   |
|--------------------|-------------------------------------------------------------|----------------------------------------------------------------------|------------------------------------------|
| Delphes cards      | /eos/experiment/fcc/hh/utils/delphescards/                  | /global/cfs/cdirs/atlas/oarakji/myFiles/delphescards/               | [ ] Not started / [ ] In progress / [ ] ✅ Done |
| Pythia cards       | /eos/experiment/fcc/hh/utils/pythiacards/                   | /global/cfs/cdirs/atlas/oarakji/myFiles/pythiacards/                | [ ] Not started / [ ] In progress / [ ] ✅ Done |
| Proc JSON          | /eos/experiment/fcc/www/data/FCCDicts/FCChh_procDict_VERSION_DETECTOR.json | /global/cfs/cdirs/atlas/oarakji/myFiles/FCCDicts/FCChh_procDict_VERSION_DETECTOR.json | [ ] Not started / [ ] In progress / [ ] ✅ Done |
| YAML Dir           | /eos/home-o/oarakji/tth/yaml/FCChh/                         | /global/cfs/cdirs/atlas/oarakji/myFiles/yaml/FCChh/                 | [ ] Not started / [ ] In progress / [ ] ✅ Done |
| Config             | /eos/experiment/fcc/hh/utils/config/                        | /global/cfs/cdirs/atlas/oarakji/myFiles/config/                     | [ ] Not started / [ ] In progress / [ ] ✅ Done |
| Other (specify)    |                                                             |                                                                      | [ ] Not started / [ ] In progress / [ ] ✅ Done |

---

*Mark status as you transfer each item and update the paths or list as needed for your project.*
```

---
