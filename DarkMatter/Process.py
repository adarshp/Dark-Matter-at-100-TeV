import re, os
import subprocess as sp
import shutil as sh
from helpers import *
from ClusterConfiguration import myClusterConfig

class Process(object):
    def __init__(
            self, name, model, decay_channel, 
            mg5_generation_syntax, energy, index):

        self.name = name
        self.model = model
        self.decay_channel = decay_channel
        self.mg5_generation_syntax = mg5_generation_syntax
        self.energy = '100_TeV'
        self.index = str(index)

        self.common_path = '/'.join([self.process_type()+'s', self.name, 
                                     self.decay_channel, self.energy, self.index])
        self.directory = '/'.join(['Events', self.common_path])

    def create_directory(self):
        proc_card = '/'.join(['Cards/proc_cards', self.common_path+ '_proc_card.dat'])
        if not os.path.exists(os.path.dirname(proc_card)):
            try:
                os.makedirs(os.path.dirname(proc_card))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        with open(proc_card, 'w') as f:
            f.write('import model {}\n'.format(self.model))
            f.write(self.mg5_generation_syntax+'\n')
            f.write('output '+self.directory)
        sp.call(['./Tools/mg5/bin/mg5_aMC', proc_card], stdout = open(os.devnull, 'w'))

    def process_type(self):
        if self.model == 'sm': return 'Background'
        else: return 'Signal'

    def copy_cards(self):
        destination = self.directory+'/Cards/'
        sh.copy('Cards/run_cards/run_card.dat', destination)
        if self.energy == '100_TeV':
            sh.copy('Cards/delphes_cards/FCChh.tcl', destination+'delphes_card.dat')
        else: 
            sh.copy('Cards/delphes_cards/delphes_card.dat', destination)

        sh.copy('Cards/run_cards/run_card.dat', destination)
        sh.copy('Cards/pythia_cards/pythia_card.dat', destination)

    def write_pbs_script(self, nruns):
        with open('submit.pbs', 'w') as f:
            f.write(myClusterConfig.pbs_script_template.format(
                    jobname = self.name,
                    email = myClusterConfig.email,
                    group_list = myClusterConfig.group_list,
                    username = myClusterConfig.username,
                    cput = str(15*nruns),
                    walltime = str(30*nruns),
                    mg5_process_dir = self.directory,
                    nruns = str(nruns),
                  ))
    
    def setup_for_generation(self, nruns, nevents):
        self.copy_cards()
        with cd(self.directory):
            self.write_pbs_script(nruns)
            modify_file('Cards/run_card.dat',set_beam_energy) 
            modify_file('Cards/run_card.dat', lambda x: re.sub(r'\d* = nev', str(nevents)+" = nev", x))

    def generate_events_locally(self, nruns = 1, nevents = 10000):
        self.setup_for_generation(nruns, nevents)
        with cd(self.directory):
            for run in range(0, nruns):
                sp.call(['./bin/generate_events','--laststep=delphes', '-f'])
                sp.call(['./bin/madevent','remove','all', 'parton', '-f'])
                sp.call(['./bin/madevent','remove','all', 'pythia', '-f'])
                sp.call('rm -rf Events/run_*/tag_*_delphes_events.root', shell = True)

    def generate_events(self, nruns = 1, nevents = 10000):
        self.setup_for_generation(nruns, nevents)
        with cd(self.directory):
            sp.call(['qsub', 'submit.pbs'], stdout = open(os.devnull, 'w')) 
