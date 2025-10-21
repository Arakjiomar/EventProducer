#!/usr/bin/env python3
import os, sys
import subprocess
import time
import EventProducer.common.utils as ut
import EventProducer.common.makeyaml as my

class send_stdhep():

#__________________________________________________________
    def __init__(self,njobs,events, process, islsf, isslurm, islocal, queue, priority, ncpus, para, version, typestdhep, training, account='', time='02:00:00', nodes='1', ntasks='1', mem='4GB'):
        self.njobs    = njobs
        self.events   = events
        self.process  = process
        self.islsf    = islsf
        self.isslurm  = isslurm
        self.islocal  = islocal
        self.queue    = queue
        self.priority = priority
        self.ncpus    = ncpus
        self.account  = account
        self.time     = time
        self.nodes    = nodes
        self.ntasks   = ntasks
        self.mem      = mem
        self.user     = os.environ['USER']
        self.para     = para
        self.version  = version
        self.typestdhep  = typestdhep
        self.training = training

#__________________________________________________________
    def send(self):
        Dir = os.getcwd()
        nbjobsSub=0

        print("njobs=",self.njobs)

        stdhepdir=self.para.stdhep_dir
        # From winter2023 onwards, the stdhep files are store in stdehp/prodTag or stdhep/prodTag/training
        if not( 'spring2021' in self.version or 'pre_fall2022' in self.version or 'dev' in self.version ):
            prodtag = self.version.replace("_training","")
            stdhepdir=stdhepdir+"/%s/"%(prodtag)
        if self.typestdhep == 'wzp6' and self.training:
            stdhepdir = stdhepdir + "training/"
        print("stdhepdir =",stdhepdir)
        gpdir=self.para.gp_dir

        acctype='FCC'
        if 'HELHC' in self.para.module_name:  acctype='HELHC'
        elif 'FCCee' in self.para.module_name:  acctype='FCCee'

        logdir=Dir+"/BatchOutputs/%s/stdhep/%s"%(acctype,self.process)
        if not ut.dir_exist(logdir):
            os.system("mkdir -p %s"%logdir)


        if not self.islocal:
             yamldir = '%s/stdhep/%s'%(self.para.yamldir,self.process)    # for pre-winter2023 tags
             if self.training:
                  yamldir = '%s/stdhep/training/%s'%(self.para.yamldir,self.process)
             if not( 'spring2021' in self.version or 'pre_fall2022' in self.version or 'dev' in self.version ):   # winter2023 and later:
                  prodtag = self.version.replace("_training","")
                  yamldir = '%s/stdhep/%s/%s'%(self.para.yamldir,prodtag,self.process)
                  if self.training:
                      yamldir = '%s/stdhep/%s/training/%s'%(self.para.yamldir,prodtag,self.process)
             print("yamldir = ",yamldir)
             if not ut.dir_exist(yamldir):
                 os.system("mkdir -p %s"%yamldir)

        if self.typestdhep == 'wzp6':
            whizardcard='%s%s.sin'%(self.para.whizardcards_dir, 'v3.0.3/'+self.process)     # Whizard 2.8.5, with Pythia6 interface
            if 'spring2021' in self.version or 'pre_fall2022' in self.version or 'dev' in self.version:
                whizardcard='%s%s.sin'%(self.para.whizardcards_dir, 'v2.8.5/'+self.process)     # Whizard 2.8.5, with Pythia6 interface
	  

        whizardcard=whizardcard.replace('_VERSION_',self.version)
        if ut.file_exist(whizardcard)==False:
            print ('Whizard card does not exist: ',whizardcard,' , exit')
            if '_EvtGen_' not in self.process:
                sys.exit(3)


        if self.islsf==False and self.isslurm==False and self.islocal==False:
            print ("Submit issue : LSF nor SLURM nor Local flag defined !!!")
            sys.exit(3)

        slurm_scripts_list=[]
        while nbjobsSub<self.njobs:
            if self.typestdhep == 'wzp6':
                uid = ut.getuid2()
                if self.training: 
                      #print("---- INFO: using getuidtraining")
                      uid = ut.getuidtraining()

            if not self.islocal:
                myyaml = my.makeyaml(yamldir, uid)
                if not myyaml: 
                    print ('job %s already exists'%uid)
                    continue

                outfile='%s/%s/events_%s.stdhep.gz'%(stdhepdir,self.process,uid)
                if ut.file_exist('%s/%s/events_%s.stdhep.gz'%(stdhepdir,self.process,uid)):
                    print ('already exist, continue')
                    continue

            if self.islocal:
                outfile = '%s/events_%s.stdhep.gz'%(logdir,uid)
                if ut.file_exist(outfile):
                    print ('file %s already locally exist, continue'%outfile)
                    continue


            frunname = 'job%s.sh'%(uid) 
            frunfull = '%s/%s'%(logdir,frunname)

            frun = None
            try:
                frun = open(frunfull, 'w')
            except IOError as e:
                print ("I/O error({0}): {1}".format(e.errno, e.strerror))
                time.sleep(10)
                frun = open(frunfull, 'w')
                
            subprocess.getstatusoutput('chmod 777 %s'%frunfull)
            frun.write('#!/bin/bash\n')
            frun.write('unset LD_LIBRARY_PATH\n')
            frun.write('unset PYTHONHOME\n')
            frun.write('unset PYTHONPATH\n')
            frun.write('mkdir job%s_%s\n'%(uid,self.process))
            frun.write('cd job%s_%s\n'%(uid,self.process))
            frun.write('export EOS_MGM_URL=\"root://eospublic.cern.ch\"\n')
            frun.write('source %s\n'%(self.para.defaultstack))
            #frun.write('mkdir %s\n'%(stdhepdir))
            if self.islocal==False:
                frun.write('mkdir -p %s%s\n'%(stdhepdir,self.process))
            frun.write('python /afs/cern.ch/work/f/fccsw/public/FCCutils/eoscopy.py %s thecard.sin\n'%(whizardcard))
            #frun.write('cd process/\n')
            #frun.write('./run.sh %i %i\n'%(self.events,int(uid.lstrip('0'))))
            
            frun.write('echo "n_events = %i" > header.sin \n'%(self.events))
            frun.write('echo "seed = %s"  >> header.sin \n'%(uid))
            frun.write('cat header.sin thecard.sin > card.sin \n') 

            frun.write('whizard card.sin \n')
            frun.write('echo "finished run"\n')
            frun.write('gzip proc.stdhep \n')
            #frun.write('python /afs/cern.ch/work/f/fccsw/public/FCCutils/eoscopy.py events.lhe.gz %s/%s/events_%s.lhe.gz\n'%(lhedir,self.process ,uid))
            #frun.write('xrdcp -N -v proc.stdhep.gz root://eospublic.cern.ch/%s/%s/events_%s.lhe.gz\n'%(stdhepdir,self.process ,uid))
            frun.write('python /afs/cern.ch/work/f/fccsw/public/FCCutils/eoscopy.py proc.stdhep.gz %s\n'%(outfile))
            frun.write('echo "stdhep.gz file successfully copied on eos"\n')

            frun.write('cd ..\n')
            #frun.write('rm -rf job%s_%s\n'%(uid,self.process))
            frun.close()

            if self.islsf==True :
              cmdBatch="bsub -M 2000000 -R \"rusage[pool=2000]\" -q %s -o %s -cwd %s %s" %(self.queue,logdir+'/job%s/'%(uid),logdir+'/job%s/'%(uid),logdir+'/'+frunname)
              #print cmdBatch

              batchid=-1
              job,batchid=ut.SubmitToLsf(cmdBatch,10,"%i/%i"%(nbjobsSub,self.njobs))
              nbjobsSub+=job
            elif self.isslurm==True :
              slurm_scripts_list.append(frunfull)
              nbjobsSub+=1

            elif self.islocal==True:
                print ('will run locally')
                nbjobsSub+=1
                os.system('%s'%frunfull)

        if self.isslurm==True :
            # Submit individual SLURM jobs for each script
            nbjobsSub=0
            for script_path in slurm_scripts_list:
                # Create SLURM batch script that includes Perlmutter setup
                slurm_script_name = script_path.replace('.sh', '_slurm.sh')
                
                try:
                    fslurm = open(slurm_script_name, 'w')
                except IOError as e:
                    print ("I/O error({0}): {1}".format(e.errno, e.strerror))
                    time.sleep(10)
                    fslurm = open(slurm_script_name, 'w')
                
                # Write SLURM header with Perlmutter setup
                fslurm.write('#!/bin/bash\n')
                fslurm.write('#SBATCH --job-name=stdhep_%s\n' % self.process)
                fslurm.write('#SBATCH --partition=%s\n' % self.queue)
                if self.account:
                    fslurm.write('#SBATCH --account=%s\n' % self.account)
                fslurm.write('#SBATCH --time=%s\n' % self.time)
                fslurm.write('#SBATCH --nodes=%s\n' % self.nodes)
                fslurm.write('#SBATCH --ntasks=%s\n' % self.ntasks)
                fslurm.write('#SBATCH --cpus-per-task=%s\n' % self.ncpus)
                fslurm.write('#SBATCH --mem=%s\n' % self.mem)
                fslurm.write('#SBATCH --output=%s/slurm_job.%%j.out\n' % logdir)
                fslurm.write('#SBATCH --error=%s/slurm_job.%%j.err\n' % logdir)
                fslurm.write('\n')
                
                # Add Perlmutter environment setup
                fslurm.write('# Perlmutter environment and authentication setup\n')
                fslurm.write('source /global/cfs/cdirs/atlas/scripts/setupATLAS.sh\n')
                fslurm.write('setupATLAS -c el9+batch\n')
                fslurm.write('voms-proxy-init -voms atlas\n')
                fslurm.write('source ./init.sh\n')
                fslurm.write('\n')
                fslurm.write('# Check VOMS proxy was created\n')
                fslurm.write('voms-proxy-info --exists || exit 1\n')
                fslurm.write('\n')
                
                # Execute the original script
                fslurm.write('# Execute the EventProducer job\n')
                fslurm.write('bash %s\n' % script_path)
                fslurm.close()
                
                subprocess.getstatusoutput('chmod +x %s' % slurm_script_name)
                
                # Submit the SLURM job
                cmdBatch="sbatch %s" % slurm_script_name
                print (cmdBatch)
                job=ut.SubmitToSlurm(cmdBatch,10,"%i/%i"%(nbjobsSub,len(slurm_scripts_list)))
                nbjobsSub+=job
    
        print ('succesfully sent %i  job(s)'%nbjobsSub)

