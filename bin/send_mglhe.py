#python bin/run.py --FCC --LHE --send --version fcc_v02 -p dummy --typelhe mg --mg5card pp_hh.mg5 --model loop_sm_hh.tar -N 2 -n 10000 -q workday --condor

#!/usr/bin/env python
import os, sys
import subprocess
import time
import EventProducer.common.utils as ut
import EventProducer.common.makeyaml as my

class send_mglhe():

#__________________________________________________________
    def __init__(self, islsf, isslurm, mg5card, cutfile, model, para, procname, njobs, nev, queue, priority, ncpus, do_EL7, useV3=False, useV342=False, account='', time='02:00:00', nodes='1', ntasks='1', mem='4GB'):
        self.islsf     = islsf
        self.isslurm   = isslurm
        self.account   = account
        self.time      = time
        self.nodes     = nodes
        self.ntasks    = ntasks
        self.mem       = mem
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

        if self.islsf==False and self.isslurm==False:
            print ("Submit issue : LSF nor SLURM flag defined !!!")
            sys.exit(3)

        slurm_job_params=[]
        while nbjobsSub<self.njobs:
            uid = ut.getuid2()
            myyaml = my.makeyaml(yamldir, uid)
            if not myyaml: 
                print ('job %s already exists'%uid)
                continue

            if ut.file_exist('%s/%s/events_%s.lhe.gz'%(outdir,self.procname,uid)):
                print ('already exist, continue')
                continue
    
            print ('Submitting job '+str(nbjobsSub)+' out of '+str(self.njobs))
            seed = str(uid)
            
            basename =  self.procname+ '_'+seed

            cwd = os.getcwd()
            script = cwd + '/bin/submitMG.sh '
            if self.useV3:
                script = cwd + '/bin/submitMG_v3.sh '
            if self.useV342:
                script = cwd + '/bin/submitMG_v3_4_2.sh '
            if self.islsf==True :
              cmdBatch = 'bsub -o '+jobsdir+'/std/'+basename +'.out -e '+jobsdir+'/std/'+basename +'.err -q '+self.queue
              cmdBatch +=' -J '+basename +' "'+script + mg5card+' '+self.procname+' '+outdir+' '+seed+' '+str(self.nev)+' '+cuts+' '+model+'"'

              print (cmdBatch)

              batchid=-1
              job,batchid=ut.SubmitToLsf(cmdBatch,10,1)
              nbjobsSub+=job
            elif self.isslurm==True :
              slurm_job_params.append((mg5card, self.procname, outdir, seed, str(self.nev), cuts, model, script, basename))
              nbjobsSub+=1

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
                if self.account:
                    fslurm.write('#SBATCH --account=%s\n' % self.account)
                fslurm.write('#SBATCH --time=%s\n' % self.time)
                # Use single task configuration for Perlmutter compatibility
                fslurm.write('#SBATCH --ntasks=1\n')
                fslurm.write('#SBATCH --cpus-per-task=%s\n' % self.ncpus)
                # Remove memory specification to let SLURM use default allocation per CPU
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
                
                subprocess.getstatusoutput('chmod +x %s' % slurm_script_name)
                
                # Submit the SLURM job
                cmdBatch="sbatch %s" % slurm_script_name
                print (cmdBatch)
                job=ut.SubmitToSlurm(cmdBatch,10,"%i/%i"%(nbjobsSub,len(slurm_job_params)))
                nbjobsSub+=job

        print ('succesfully sent %i  job(s)'%nbjobsSub)

