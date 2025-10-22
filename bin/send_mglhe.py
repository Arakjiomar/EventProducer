#python bin/run.py --FCC --LHE --send --version fcc_v02 -p dummy --typelhe mg --mg5card pp_hh.mg5 --model loop_sm_hh.tar -N 2 -n 10000 -q workday --condor

#!/usr/bin/env python
import os, sys
import subprocess
import time
import random
import EventProducer.common.utils as ut
import EventProducer.common.makeyaml as my

class send_mglhe():

#__________________________________________________________
<<<<<<< HEAD
    def __init__(self, islsf, isslurm, mg5card, cutfile, model, para, procname, njobs, nev, queue, priority, ncpus, do_EL7, useV3=False, useV342=False, account='', time='02:00:00', nodes='1', ntasks='1', mem='4GB', islocal=False):
        self.islsf     = islsf
        self.isslurm   = isslurm
        self.islocal   = islocal
        self.account   = account
        self.time      = time
        self.nodes     = nodes
        self.ntasks    = ntasks
        self.mem       = mem
=======
    def __init__(self, islsf, iscondor, isslurm, mg5card, cutfile, model, para, procname, njobs, nev, queue, priority, ncpus, do_EL7, useV3=False, useV342=False, account='m3792', time='01:00:00'):
        self.islsf     = islsf
        self.iscondor  = iscondor
        self.isslurm   = isslurm
>>>>>>> origin/perlmutter-version
        self.user      = os.environ['USER']
        self.mg5card   = mg5card
        self.cutfile   = cutfile
        self.model     = model
        self.para      = para
        self.procname  = procname
        self.njobs     = njobs
        self.nev       = nev
        self.queue     = queue
        self.priority  = priority
        self.ncpus     = ncpus
        self.do_EL7    = do_EL7
        self.useV3     = useV3
        self.useV342   = useV342
        self.account   = account
        self.time      = time

#__________________________________________________________
    def send(self):
        Dir = os.getcwd()
        nbjobsSub=0

        # output dir
        outdir=self.para.lhe_dir

        acctype='FCC'
        if 'HELHC' in self.para.module_name:  acctype='HELHC'
        elif 'FCCee' in self.para.module_name:  acctype='FCCee'

        logdir=Dir+"/BatchOutputs/%s/lhe/%s"%(acctype,self.procname)

        if not ut.dir_exist(logdir):
            os.system("mkdir -p %s"%logdir)

        yamldir = '%s/lhe/%s'%(self.para.yamldir,self.procname)
        if not ut.dir_exist(yamldir):
            os.system("mkdir -p %s"%yamldir)

        outdir  = os.path.abspath(outdir)
        mg5card = os.path.abspath(self.mg5card)
        cuts    = os.path.abspath(self.cutfile)
        model   = os.path.abspath(self.model)

        jobsdir = './BatchOutputs/%s/lhe/%s/'%(acctype,self.procname)

        if not os.path.exists(jobsdir):
           os.makedirs(jobsdir)
           os.makedirs(jobsdir+'/std/')
           os.makedirs(jobsdir+'/cfg/')

<<<<<<< HEAD
        if self.islsf==False and self.isslurm==False and self.islocal==False:
            print ("Submit issue : LSF, SLURM, nor LOCAL flag defined !!!")
            sys.exit(3)

        slurm_job_params=[]
        
        if self.islocal==True:
            # For local execution, create simple job parameters without YAML management
            for i in range(self.njobs):
                seed = str(random.randint(100000, 999999))  # Random seed generation for local jobs
                basename = f"{self.procname}_{seed}"
                
                # Skip if output already exists
                if ut.file_exist('%s/%s/events_%s.lhe.gz'%(outdir,self.procname,seed)):
                    print ('already exist for %s, skipping'%seed)
                    continue
                
                cuts = self.cutfile if self.cutfile else './null'
                model = self.model if self.model else './null'
                
                cwd = os.getcwd()
                script = cwd + '/bin/submitMG.sh '
                if self.useV3:
                    script = cwd + '/bin/submitMG_v3.sh '
                if self.useV342:
                    script = cwd + '/bin/submitMG_v3_4_2.sh '
                
                slurm_job_params.append((self.mg5card, self.procname, outdir, seed, str(self.nev), cuts, model, script, basename))
        else:
            # Original logic for LSF/SLURM
            while nbjobsSub<self.njobs:
                uid = ut.getuid2()
                myyaml = my.makeyaml(yamldir, uid)
                if not myyaml: 
                    print ('job %s already exists'%uid)
                    continue
=======
        if self.islsf==False and self.iscondor==False and self.isslurm==False:
            print ("Submit issue : LSF, CONDOR, nor SLURM flag defined !!!")
            sys.exit(3)

        condor_file_params_str=[]
        slurm_file_params_str=[]
        while nbjobsSub<self.njobs:
            uid = ut.getuid2()
            myyaml = my.makeyaml(yamldir, uid)
            if not myyaml: 
                print ('job %s already exists'%uid)
                continue
>>>>>>> origin/perlmutter-version

                if ut.file_exist('%s/%s/events_%s.lhe.gz'%(outdir,self.procname,uid)):
                    print ('already exist, continue')
                    continue
        
                print ('Submitting job '+str(nbjobsSub)+' out of '+str(self.njobs))
                seed = str(uid)
                
                basename =  self.procname+ '_'+seed

<<<<<<< HEAD
                cwd = os.getcwd()
                script = cwd + '/bin/submitMG.sh '
                if self.useV3:
                    script = cwd + '/bin/submitMG_v3.sh '
                if self.useV342:
                    script = cwd + '/bin/submitMG_v3_4_2.sh '
                if self.islsf==True :
                  cmdBatch = 'bsub -o '+jobsdir+'/std/'+basename +'.out -e '+jobsdir+'/std/'+basename +'.err -q '+self.queue
                  cmdBatch +=' -J '+basename +' "'+script + self.mg5card+' '+self.procname+' '+outdir+' '+seed+' '+str(self.nev)+' '+cuts+' '+model+'"'
=======
            cwd = os.getcwd()
            script = cwd + '/bin/submitMG.sh '
            if self.useV3:
                script = cwd + '/bin/submitMG_v3.sh '
            if self.useV342:
                script = cwd + '/bin/submitMG_v3_4_2.sh '
            if self.isslurm:
                script = cwd + '/bin/submitMG_slurm.sh '
            if self.islsf==True :
              cmdBatch = 'bsub -o '+jobsdir+'/std/'+basename +'.out -e '+jobsdir+'/std/'+basename +'.err -q '+self.queue
              cmdBatch +=' -J '+basename +' "'+script + mg5card+' '+self.procname+' '+outdir+' '+seed+' '+str(self.nev)+' '+cuts+' '+model+'"'
>>>>>>> origin/perlmutter-version

                  print (cmdBatch)

<<<<<<< HEAD
                  batchid=-1
                  job,batchid=ut.SubmitToLsf(cmdBatch,10,1)
                  nbjobsSub+=job
                elif self.isslurm==True :
                  cuts = self.cutfile if self.cutfile else './null'
                  model = self.model if self.model else './null'
                  slurm_job_params.append((self.mg5card, self.procname, outdir, seed, str(self.nev), cuts, model, script, basename))
                  nbjobsSub+=1
=======
              batchid=-1
              job,batchid=ut.SubmitToLsf(cmdBatch,10,1)
              nbjobsSub+=job
            elif self.iscondor==True :
              condor_file_params_str.append(mg5card+' '+self.procname+' '+outdir+' '+seed+' '+str(self.nev)+' '+cuts+' '+model)
              nbjobsSub+=1
            elif self.isslurm==True :
              slurm_file_params_str.append(mg5card+' '+self.procname+' '+outdir+' '+seed+' '+str(self.nev)+' '+cuts+' '+model)
              nbjobsSub+=1
>>>>>>> origin/perlmutter-version

        if self.isslurm==True :
            # Submit individual SLURM jobs
            nbjobsSub=0
            for job_params in slurm_job_params:
                mg5card, procname, outdir, seed, nev, cuts, model, script, basename = job_params
                
                # Create SLURM batch script
                slurm_script_name = '%s/slurm_%s.sh' % (jobsdir, basename)
                
                try:
                    fslurm = open(slurm_script_name, 'w')
                except IOError as e:
                    print ("I/O error({0}): {1}".format(e.errno, e.strerror))
                    time.sleep(10)
                    fslurm = open(slurm_script_name, 'w')
                
                # Write SLURM header with Perlmutter setup
                fslurm.write('#!/bin/bash\n')
                fslurm.write('#SBATCH --job-name=mglhe_%s\n' % basename)
                fslurm.write('#SBATCH --partition=%s\n' % self.queue)
                # Required constraint for Perlmutter CPU nodes
                fslurm.write('#SBATCH --constraint=cpu\n')
                # Account is required for Perlmutter
                if self.account:
                    fslurm.write('#SBATCH --account=%s\n' % self.account)
                else:
                    fslurm.write('#SBATCH --account=atlas\n')  # Default account
                fslurm.write('#SBATCH --time=%s\n' % self.time)
                # Use single task configuration for Perlmutter compatibility
                fslurm.write('#SBATCH --ntasks=1\n')
                fslurm.write('#SBATCH --cpus-per-task=%s\n' % self.ncpus)
                # Add memory specification for Perlmutter (4GB per CPU is typical)
                fslurm.write('#SBATCH --mem=%s\n' % self.mem)
                fslurm.write('#SBATCH --output=%s/std/%s.out\n' % (jobsdir, basename))
                fslurm.write('#SBATCH --error=%s/std/%s.err\n' % (jobsdir, basename))
                fslurm.write('\n')
                
                # Add Perlmutter environment setup
                fslurm.write('# Perlmutter environment setup\n')
                fslurm.write('source /global/homes/o/oarakji/setup_complete_env.sh\n')
                fslurm.write('\n')
                
                # Execute the MG5 script with parameters
                fslurm.write('# Execute the MG5 job\n')
                fslurm.write('%s %s %s %s %s %s %s %s\n' % (script, mg5card, procname, outdir, seed, nev, cuts, model))
                fslurm.close()
                
                os.system('chmod +x %s' % slurm_script_name)
                
                # Submit the SLURM job
                cmdBatch="sbatch %s" % slurm_script_name
                print (cmdBatch)
                job=ut.SubmitToSlurm(cmdBatch,10,"%i/%i"%(nbjobsSub,len(slurm_job_params)))
                nbjobsSub+=job
        
        if self.islocal==True :
            # Execute jobs locally
            nbjobsSub=0
            for job_params in slurm_job_params:
                mg5card, procname, outdir, seed, nev, cuts, model, script, basename = job_params
                
                print(f"Running local job {nbjobsSub+1}/{len(slurm_job_params)}: {basename}")
                
                # Execute the MG5 script directly with absolute paths
                abs_mg5card = os.path.abspath(mg5card) if not os.path.isabs(mg5card) else mg5card
                cmd = f'{script} {abs_mg5card} {procname} {outdir} {seed} {nev} {cuts} {model}'
                print(f"Executing: {cmd}")
                
                # Create log directory
                logdir = f"{jobsdir}/std"
                os.makedirs(logdir, exist_ok=True)
                
                # Run the command and capture output
                import subprocess
                with open(f'{logdir}/{basename}.out', 'w') as stdout_file, \
                     open(f'{logdir}/{basename}.err', 'w') as stderr_file:
                    
                    result = subprocess.run(cmd, shell=True, stdout=stdout_file, stderr=stderr_file, cwd=os.getcwd())
                    
                    if result.returncode == 0:
                        print(f"Local job {basename} completed successfully")
                        nbjobsSub += 1
                    else:
                        print(f"Local job {basename} failed with return code {result.returncode}")

        if self.isslurm==True :
            # parameter file
            fparamname_slurm = 'job_params_mglhe.txt'
            fparamfull_slurm = '%s/%s'%(logdir,fparamname_slurm)
            fparam_slurm = None
            try:
                fparam_slurm = open(fparamfull_slurm, 'w')
            except IOError as e:
                print ("I/O error({0}): {1}".format(e.errno, e.strerror))
                time.sleep(10)
                fparam_slurm = open(fparamfull_slurm, 'w')
            for line in slurm_file_params_str:
                fparam_slurm.write('%s\n'%line)
            fparam_slurm.close()
            
            # slurm config
            frunname_slurm = 'job_desc_mglhe.sh'
            frunfull_slurm = '%s/%s'%(logdir,frunname_slurm)
            frun_slurm = None
            try:
                frun_slurm = open(frunfull_slurm, 'w')
            except IOError as e:
                print ("I/O error({0}): {1}".format(e.errno, e.strerror))
                time.sleep(10)
                frun_slurm = open(frunfull_slurm, 'w')
            subprocess.getstatusoutput('chmod 755 %s'%frunfull_slurm)
            
            # Write SLURM script
            frun_slurm.write('#!/bin/bash\n')
            frun_slurm.write('#SBATCH --account=%s\n'%self.account)
            frun_slurm.write('#SBATCH --qos=%s\n'%self.queue)
            frun_slurm.write('#SBATCH --time=%s\n'%self.time)
            frun_slurm.write('#SBATCH --nodes=1\n')
            frun_slurm.write('#SBATCH --ntasks-per-node=%s\n'%self.ncpus)
            frun_slurm.write('#SBATCH --cpus-per-task=1\n')
            frun_slurm.write('#SBATCH --constraint=cpu\n')
            frun_slurm.write('#SBATCH --job-name=%s\n'%self.procname)
            frun_slurm.write('#SBATCH --output=%s/slurm_job.%%j.out\n'%logdir)
            frun_slurm.write('#SBATCH --error=%s/slurm_job.%%j.err\n'%logdir)
            frun_slurm.write('#SBATCH --array=1-%d\n'%len(slurm_file_params_str))
            frun_slurm.write('\n')
            frun_slurm.write('# Get job parameters from parameter file\n')
            frun_slurm.write('PARAMS=$(sed -n "${SLURM_ARRAY_TASK_ID}p" %s)\n'%fparamfull_slurm)
            frun_slurm.write('\n')
            frun_slurm.write('# Execute the script with parameters\n')
            frun_slurm.write('%s $PARAMS\n'%script)
            frun_slurm.close()
            
            # Submit array job
            nbjobsSub=0
            cmdBatch="sbatch %s"%frunfull_slurm
            print (cmdBatch)
            job, jobid = ut.SubmitToSlurm(cmdBatch,10,"%i/%i"%(nbjobsSub,self.njobs))
            nbjobsSub+=job

        print ('succesfully sent %i  job(s)'%nbjobsSub)

