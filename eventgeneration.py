from __future__ import division
import os
import sys
sys.path.insert(0, '../clusterpheno')
from clusterpheno.helpers import cd, modify_file, do_parallel
import subprocess as sp
import shutil as sh
from myProcesses import signals
from tqdm import tqdm
from ConfigParser import SafeConfigParser

def create_mg5_dirs(mg5_path):
    for process in tqdm(signals, dynamic_ncols = True, 
            desc = "Creating mg5 directories"):
        process.create_directory(mg5_path)

def copy_cards(run_card, pythia_card, delphes_card): 
    for process in tqdm(signals, dynamic_ncols = True,
                        desc = 'Copying cards'):
        process.copy_cards(run_card, pythia_card, delphes_card)
        # process.copy_param_card()
        # sh.copy('Cards/delphes_cards/momentumResolutionVsP.tcl', process.directory+'/Cards/')
        # sh.copy('Cards/delphes_cards/muonMomentumResolutionVsP.tcl', process.directory+'/Cards/')
        sh.copy('Cards/me5_configuration.txt', process.directory+'/Cards/')


def main():   
    parser = SafeConfigParser()
    parser.read('config.ini')
    # write_pbs_scripts(parser, 1)
    
if __name__ == '__main__':
    main()
