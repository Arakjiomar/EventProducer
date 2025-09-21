#python bin/run.py --FCC --LHE --send --version fcc_v02 -p dummy --typelhe mg --mg5card pp_hh.mg5 --model loop_sm_hh.tar -N 2 -n 10000 -q workday --condor

#!/usr/bin/env python
import os, sys
import subprocess
import time
import EventProducer.common.utils as ut
import EventProducer.common.makeyaml as my

class send_mglhe():

#__________________________________________________________
    def __init__(self, islsf, iscondor, isslurm, mg5card, cutfile, model, para, procname, njobs, nev, queue, priority, ncpus, do_EL7, useV3=False, useV342=False, account='m3792', time='01:00:00'):
        self.islsf     = islsf
        self.iscondor  = iscondor
        self.isslurm   = isslurm
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
            if self.isslurm:
                script = cwd + '/bin/submitMG_slurm.sh '
            if self.islsf==True :
              cmdBatch = 'bsub -o '+jobsdir+'/std/'+basename +'.out -e '+jobsdir+'/std/'+basename +'.err -q '+self.queue
              cmdBatch +=' -J '+basename +' "'+script + mg5card+' '+self.procname+' '+outdir+' '+seed+' '+str(self.nev)+' '+cuts+' '+model+'"'

              print (cmdBatch)

              batchid=-1
              job,batchid=ut.SubmitToLsf(cmdBatch,10,1)
              nbjobsSub+=job
            elif self.iscondor==True :
              condor_file_params_str.append(mg5card+' '+self.procname+' '+outdir+' '+seed+' '+str(self.nev)+' '+cuts+' '+model)
              nbjobsSub+=1
            elif self.isslurm==True :
              slurm_file_params_str.append(mg5card+' '+self.procname+' '+outdir+' '+seed+' '+str(self.nev)+' '+cuts+' '+model)
              nbjobsSub+=1

        if self.iscondor==True :
            # parameter file
            fparamname_condor = 'job_params_mglhe.txt'
            fparamfull_condor = '%s/%s'%(logdir,fparamname_condor)
            fparam_condor = None
            try:
                fparam_condor = open(fparamfull_condor, 'w')
            except IOError as e:
                print ("I/O error({0}): {1}".format(e.errno, e.strerror))
                time.sleep(10)
                fparam_condor = open(fparamfull_condor, 'w')
            for line in condor_file_params_str:
                fparam_condor.write('%s\n'%line)
            fparam_condor.close()
            # condor config
            frunname_condor = 'job_desc_mglhe.cfg'
            frunfull_condor = '%s/%s'%(logdir,frunname_condor)
            frun_condor = None
            try:
                frun_condor = open(frunfull_condor, 'w')
            except IOError as e:
                print ("I/O error({0}): {1}".format(e.errno, e.strerror))
                time.sleep(10)
                frun_condor = open(frunfull_condor, 'w')
            subprocess.getstatusoutput('chmod 777 %s'%frunfull_condor)
            #
            frun_condor.write('executable     = %s\n'%script)
            frun_condor.write('Log            = %s/condor_job.%s.$(ClusterId).$(ProcId).log\n'%(logdir,str(uid)))
            frun_condor.write('Output         = %s/condor_job.%s.$(ClusterId).$(ProcId).out\n'%(logdir,str(uid)))
            frun_condor.write('Error          = %s/condor_job.%s.$(ClusterId).$(ProcId).error\n'%(logdir,str(uid)))

            if self.do_EL7:
                print("Info: requested to run in centos7 container.")
                frun_condor.write('MY.WantOS = "el7"\n')
                frun_condor.write('environment    = "LS_SUBCWD=%s"\n'%logdir) 
            else:
                frun_condor.write('getenv         = True\n')
                frun_condor.write('environment    = "LS_SUBCWD=%s"\n'%logdir) # not sure
                frun_condor.write('requirements   = ( (OpSysAndVer =?= "AlmaLinux9") && (Machine =!= LastRemoteHost) )\n')

            frun_condor.write('on_exit_remove = (ExitBySignal == False) && (ExitCode == 0)\n')
            frun_condor.write('max_retries    = 1\n')
            frun_condor.write('+JobFlavour    = "%s"\n'%self.queue)
            frun_condor.write('+AccountingGroup = "%s"\n'%self.priority)
            frun_condor.write('RequestCpus = %s\n'%self.ncpus)
            frun_condor.write('queue arguments from %s\n'%fparamfull_condor)
            frun_condor.close()
            #
            nbjobsSub=0
            cmdBatch="condor_submit %s"%frunfull_condor
            print (cmdBatch)
            job=ut.SubmitToCondor(cmdBatch,10,"%i/%i"%(nbjobsSub,self.njobs))
            nbjobsSub+=job

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

