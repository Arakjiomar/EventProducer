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
