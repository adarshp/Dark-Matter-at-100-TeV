import subprocess
import shutil as sh
import os
from Process import Process
from templates import *
from helper_functions import cd, modify_file
import glob

devnull = open(os.devnull, 'w')

class SignalProcess(Process):

    def __init__(self, mass_combination_tuple):
        self.process_type = "Signal"
        self.mass_combination_tuple = mass_combination_tuple
        self.higgsino_mass = mass_combination_tuple[0]
        self.bino_mass = mass_combination_tuple[1]
        self.name = '_'.join([str(int(self.higgsino_mass)), 'GeV', 'Higgsino',
                              str(int(self.bino_mass)), 'GeV', 'Bino'])
        self.wino_mass = 3000.
        self.tan_beta = 10.0
        self.proc_card_path = "Cards/proc_cards/"+self.name+"_proc_card.dat"
        self.output_directory = "Events/"+self.process_type+"s/"+self.name
        self.mg5_generation_syntax = """\
        import model mssm-full
        generate p p > n2 n3, (n2 > n1 z, z > l+ l-), (n3 > n1 h1, h1 > b b~)
        add process p p > n2 n3, (n3 > n1 z, z > l+ l-), (n2 > n1 h1, h1 > b b~)
        """

        self.run_card = "Cards/run_cards/signal_run_card.dat"
        self.param_card = None
        self.xsection = self.get_xsection()

    def make_original_input_list(self, analysis_directory):
        """ Gathers filepaths for the events and writes them to the Input sub-
        directory of the analysis directory. """

        with cd(self.output_directory+'/Events'):
            cwd = os.getcwd()
            inputfiles = glob.glob('*/*.lhco.gz')
            inputfiles = [cwd+'/'+path for path in inputfiles]

        with cd(analysis_directory):
            with open('Input/Originals/'+self.name, 'w') as f:
                [f.write(filepath+'\n') for filepath in inputfiles]

    def copy_param_card(self):
        self.param_card = 'Cards/param_cards/'+self.name+'_param_card.dat'
        sh.copy(self.param_card, self.output_directory+'/Cards/param_card.dat')


    def get_xsection(self):
        with open('prospino_output/'+self.name+'_xsection.dat', 'r') as f:
            xs = float(f.readlines()[0].split()[-1:][0])

        xs = xs*1000.0 # Convert from attobarns to fb
        xs = xs*0.58 # Apply h->bb branching ratio
        xs = xs*0.067 # Apply Z->ll branching ratio
        xs = xs*0.5 # Apply Goldstone equivalence theorem

        return xs
