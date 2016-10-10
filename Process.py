import os
import re
import logging
import glob

import pandas as pd
import subprocess as sp
import shutil as sh

from sklearn.cross_validation import train_test_split
from helper_functions import cd, modify_file

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(levelname)s: %(message)s')

class Process:

    delphes_card = "Cards/delphes_cards/delphes_card.dat"

    def __init__(self, name, process_type):
        self.name = name
        self.process_type = process_type
        self.mg5_generation_syntax = None
        self.proc_card_path = "Cards/proc_cards/"+self.name+"_proc_card.dat"
        self.output_directory = "Events/"+self.process_type+"s/"+self.name
        self.xsection = None
        self.training_set = None
        self.test_set = None

    def copy_delphes_card(self):
        sh.copy(self.delphes_card, self.output_directory+'/Cards/delphes_card.dat')

    def copy_run_card(self):
        sh.copy(self.run_card, self.output_directory+'/Cards/run_card.dat')

    def create_mg5_process_directory(self, relative_mg5_path):
        """ 
        Create MadGraph5 process directory 
        
        Parameters
        ----------
        process_name : String
            The name of the process. 
        
        proc_card : String
            Relative path to the file containing the MadGraph5 commands, typically named
            something like ``proc_card.dat``.

        output_directory : String
            Directory in which the MadGraph process directory is to be placed.
        """

        with open(self.proc_card_path, 'w') as f:
            f.write(self.mg5_generation_syntax)
            f.write('output '+self.output_directory)

        devnull = open(os.devnull, 'w')
        sp.call(['./'+relative_mg5_path+'/bin/mg5_aMC', self.proc_card_path],
                stdout = devnull)
                

    def generate_events(self, nevents):
        """ Modify the run card to generate the specified number of events.

        Args:
            nevents (int) : The number of events to generate. """

        with cd(self.output_directory):
            devnull = open(os.devnull, 'w')
            modify_file('Cards/run_card.dat', 
                lambda x: re.sub(r'\d* = nev', str(int(nevents))+" = nev", x))
            sp.call(['./bin/generate_events', '-f', '--laststep=delphes'], stdout = devnull)
            sp.call(['./bin/madevent','remove', 'all', 'parton', '-f'])
            sp.call(['./bin/madevent','remove', 'all', 'pythia', '-f'])
            sp.call('rm Events/*/*.root', shell = True)
    
    def make_original_input_list(self, analysis_directory):
        """ Gathers filepaths for the events and writes them to the Input sub-
        directory of the analysis directory. """

        with cd(self.output_directory):
            cwd = os.getcwd()
            inputfiles = glob.glob('*/*/*.lhco.gz')
            inputfiles = [cwd+'/'+path for path in inputfiles]

        with cd(analysis_directory):
            with open('Input/Originals/'+self.name, 'w') as f:
                [f.write(filepath+'\n') for filepath in inputfiles]

    def make_skimmed_input_list(self, analysis_directory):
        """ Gathers filepaths for the events and writes them to the Input sub-
        directory of the analysis directory. """

        with cd('Preselection/Output'):
            cwd = os.getcwd()
            inputfiles = glob.glob(self.name+'_skimmed.lhco')
            inputfiles = [cwd+'/'+path for path in inputfiles]

        with cd(analysis_directory):
            with open('Input/Skimmed/'+self.name+'_skimmed', 'w') as f:
                [f.write(filepath+'\n') for filepath in inputfiles]

    def analyze_originals(self, analysis_directory, analysis_name):
        devnull = open(os.devnull, 'w')

        with cd(analysis_directory+'/Build/'):
            sp.call('./MadAnalysis5job ../Input/Originals/'+
                    self.name, shell=True, stdout = devnull, stderr = devnull)
                    
        if os.path.exists(analysis_directory+'/Output/'+self.name):
            with cd(analysis_directory+'/Output/'+self.name):
                sp.call(['mv', 'Analysis_0', analysis_name])

    def analyze_skimmed(self, analysis_directory, analysis_name):
        devnull = open(os.devnull, 'w')

        with cd(analysis_directory+'/Build/'):
            sp.call('./MadAnalysis5job ../Input/Skimmed/'+
                    self.name+'_skimmed', shell=True, stdout = devnull, stderr = devnull)
                    
        if os.path.exists(analysis_directory+'/Output/'+self.name+'_skimmed'):
            with cd(analysis_directory+'/Output/'+self.name+'_skimmed'):
                sp.call(['mv', 'Analysis_0', analysis_name])

    def feature_array(self, features):
        return pd.read_csv('Make_ML_Arrays/Output/{}_array.txt'.format(self.name),
                usecols = features)

    def get_train_test_data(self, features, train_size):
        """ Split the feature array into training and test splits,
        specifying the fraction to be used as test split. """
        self.training_set, self.test_set = train_test_split(self.feature_array(features),
                train_size = train_size)
