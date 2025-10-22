#!/usr/bin/env python3
import os, sys
import subprocess
import time
import EventProducer.common.utils as ut
import EventProducer.common.makeyaml as my

class send_lhe():

#__________________________________________________________
<<<<<<< HEAD
    def __init__(self,njobs,events, process, islsf, isslurm, queue, priority, ncpus, para, typelhe, account='', time='02:00:00', nodes='1', ntasks='1', mem='4GB'):
=======
    def __init__(self,njobs,events, process, islsf, iscondor, isslurm, queue, priority, ncpus, para, typelhe, account='m3792', time='01:00:00'):
>>>>>>> origin/perlmutter-version
        self.njobs    = njobs
        self.events   = events
        self.process  = process
        self.islsf    = islsf
<<<<<<< HEAD
=======
        self.iscondor = iscondor
>>>>>>> origin/perlmutter-version
        self.isslurm  = isslurm
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
        self.typelhe  = typelhe
        self.account  = account
        self.time     = time

#__________________________________________________________
    def send(self):
        Dir = os.getcwd()
        nbjobsSub=0

        gplist=self.para.gridpacklist
        lhedir=self.para.lhe_dir
        gpdir=self.para.gp_dir

        gptotest='%s/%s.tar.gz'%(gpdir,self.process)
        if ut.file_exist(gptotest)==False:
            print ('Gridpack=======',gptotest,'======= does not exist')
            sys.exit(3)

        try:
            gplist[self.process]
        except KeyError as e:
            print ('process %s does not exist as gridpack, exit'%self.process)
            sys.exit(3)

        acctype='FCC'
        if 'HELHC' in self.para.module_name:  acctype='HELHC'
        elif 'FCCee' in self.para.module_name:  acctype='FCCee'

        logdir=Dir+"/BatchOutputs/%s/lhe/%s"%(acctype,self.process)
        if not ut.dir_exist(logdir):
            os.system("mkdir -p %s"%logdir)


        yamldir = '%s/lhe/%s'%(self.para.yamldir,self.process)
        if not ut.dir_exist(yamldir):
            os.system("mkdir -p %s"%yamldir)


<<<<<<< HEAD
        if self.islsf==False and self.isslurm==False:
            print ("Submit issue : LSF nor SLURM flag defined !!!")
            sys.exit(3)

        slurm_scripts_list=[]
=======
        if self.islsf==False and self.iscondor==False and self.isslurm==False:
            print ("Submit issue : LSF, CONDOR, nor SLURM flag defined !!!")
            sys.exit(3)

        condor_file_str=''
        slurm_file_str=''
>>>>>>> origin/perlmutter-version
        while nbjobsSub<self.njobs:
            if self.typelhe == 'gp_mg':
                uid = ut.getuid2()
            elif self.typelhe == 'gp_pw':
                uid = ut.getuid3()

            myyaml = my.makeyaml(yamldir, uid)
            if not myyaml: 
                print ('job %s already exists'%uid)
                continue

            if ut.file_exist('%s/%s/events_%s.lhe.gz'%(lhedir,self.process,uid)):
                print ('already exist, continue')
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
            # frun.write('unset PYTHONPATH\n')
            frun.write('mkdir job%s_%s\n'%(uid,self.process))
            frun.write('cd job%s_%s\n'%(uid,self.process))
            frun.write('export EOS_MGM_URL=\"root://eospublic.cern.ch\"\n')
            frun.write('source %s\n'%(self.para.defaultstack))
            frun.write('mkdir %s\n'%(lhedir))
            frun.write('mkdir %s%s\n'%(lhedir,self.process))
            frun.write('python /afs/cern.ch/work/f/fccsw/public/FCCutils/eoscopy.py %s/%s.tar.gz .\n'%(gpdir,self.process))
            frun.write('tar -zxf %s.tar.gz\n'%self.process)
            
            #different dir structure in powheg gridpacks, compared to mg -> ONLY IN THE NEW ONES!
            # if self.typelhe == 'gp_pw':
            #     frun.write('./runcmsgrid.sh %i %i 8\n'%(self.events,int(uid.lstrip('0'))))
            #     frun.write('echo "finished run"\n')
            #     frun.write('gzip cmsgrid_final.lhe\n')
            #     frun.write('xrdcp -N -v cmsgrid_final.lhe.gz root://eospublic.cern.ch/%s/%s/events_%s.lhe.gz\n'%(lhedir,self.process ,uid))

            # else:
            #     frun.write('cd process/\n')
            #     frun.write('./run.sh %i %i\n'%(self.events,int(uid.lstrip('0'))))
            #     frun.write('echo "finished run"\n')
            #     #frun.write('python /afs/cern.ch/work/f/fccsw/public/FCCutils/eoscopy.py events.lhe.gz %s/%s/events_%s.lhe.gz\n'%(lhedir,self.process ,uid))
            #     frun.write('xrdcp -N -v events.lhe.gz root://eospublic.cern.ch/%s/%s/events_%s.lhe.gz\n'%(lhedir,self.process ,uid))
            
            #TEMP
            #frun.write('cd process/\n')
            frun.write('export LHAPDF_DATA_PATH=/global/cfs/cdirs/atlas/oarakji/myFiles/lhapdfsets/\n')
            frun.write('./run.sh %i %i\n'%(self.events,int(uid.lstrip('0'))))
            frun.write('echo "finished run"\n')
            #frun.write('python /afs/cern.ch/work/f/fccsw/public/FCCutils/eoscopy.py events.lhe.gz %s/%s/events_%s.lhe.gz\n'%(lhedir,self.process ,uid))
            frun.write('cp events.lhe.gz /%s/%s/events_%s.lhe.gz\n'%(lhedir,self.process ,uid))
            
            frun.write('echo "lhe file successfully copied on eos"\n')

            frun.write('cd ..\n')
            frun.write('rm -rf job%s_%s\n'%(uid,self.process))
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
            elif self.isslurm==True :
              slurm_file_str+=frunfull+" "
              nbjobsSub+=1

        if self.isslurm==True :
            # Submit individual SLURM jobs for each script
            nbjobsSub=0
<<<<<<< HEAD
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
                fslurm.write('#SBATCH --job-name=lhe_%s\n' % self.process)
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
=======
            cmdBatch="condor_submit %s"%frunfull_condor
            print (cmdBatch)
            job=ut.SubmitToCondor(cmdBatch,10,"%i/%i"%(nbjobsSub,self.njobs))
            nbjobsSub+=job    

        if self.isslurm==True :
            # clean string
            slurm_file_str=slurm_file_str.replace("//","/")
            #
            frunname_slurm = 'job_desc_lhe.sh'
            frunfull_slurm = '%s/%s'%(logdir,frunname_slurm)
            frun_slurm = None
            try:
                frun_slurm = open(frunfull_slurm, 'w')
            except IOError as e:
                print ("I/O error({0}): {1}".format(e.errno, e.strerror))
                time.sleep(10)
                frun_slurm = open(frunfull_slurm, 'w')
            subprocess.getstatusoutput('chmod 755 %s'%frunfull_slurm)
            
            # Write SLURM script for array job
            frun_slurm.write('#!/bin/bash\n')
            frun_slurm.write('#SBATCH --account=%s\n'%self.account)
            frun_slurm.write('#SBATCH --qos=%s\n'%self.queue)
            frun_slurm.write('#SBATCH --time=%s\n'%self.time)
            frun_slurm.write('#SBATCH --nodes=1\n')
            frun_slurm.write('#SBATCH --ntasks-per-node=%s\n'%self.ncpus)
            frun_slurm.write('#SBATCH --cpus-per-task=1\n')
            frun_slurm.write('#SBATCH --constraint=cpu\n')
            frun_slurm.write('#SBATCH --job-name=%s\n'%self.process)
            frun_slurm.write('#SBATCH --output=%s/slurm_lhe.%%A_%%a.out\n'%logdir)
            frun_slurm.write('#SBATCH --error=%s/slurm_lhe.%%A_%%a.err\n'%logdir)
            
            # Get list of scripts and create array
            script_list = slurm_file_str.strip().split()
            frun_slurm.write('#SBATCH --array=1-%d\n'%len(script_list))
            frun_slurm.write('\n')
            frun_slurm.write('# Array of script paths\n')
            frun_slurm.write('SCRIPTS=(\n')
            for script in script_list:
                frun_slurm.write('    "%s"\n'%script)
            frun_slurm.write(')\n')
            frun_slurm.write('\n')
            frun_slurm.write('# Execute the script for this array task\n')
            frun_slurm.write('SCRIPT_PATH="${SCRIPTS[$((SLURM_ARRAY_TASK_ID-1))]}"\n')
            frun_slurm.write('chmod +x "$SCRIPT_PATH"\n')
            frun_slurm.write('"$SCRIPT_PATH"\n')
            frun_slurm.close()
            #
            nbjobsSub=0
            cmdBatch="sbatch %s"%frunfull_slurm
            print (cmdBatch)
            job, jobid = ut.SubmitToSlurm(cmdBatch,10,"%i/%i"%(nbjobsSub,self.njobs))
            nbjobsSub+=job    
>>>>>>> origin/perlmutter-version
    
        print ('succesfully sent %i  job(s)'%nbjobsSub)

