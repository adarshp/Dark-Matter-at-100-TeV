#!/usr/bin/env python
from __future__ import division
import os
import sys
sys.path.insert(0, '/extra/adarsh/clusterpheno')
from clusterpheno.helpers import cd, modify_file, do_parallel
import subprocess as sp
import shutil as sh
from myProcesses import signals
from tqdm import tqdm
from ConfigParser import SafeConfigParser

def copy_cards(signal):
        signal.copy_cards('Cards/run_cards/run_card.dat',
                           'Cards/pythia_cards/pythia_card.dat',
                           'Cards/delphes_cards/FCChh.tcl')
        signal.copy_param_card()
        sh.copy('Cards/delphes_cards/momentumResolutionVsP.tcl', signal.directory+'/Cards/')
        sh.copy('Cards/delphes_cards/muonMomentumResolutionVsP.tcl', signal.directory+'/Cards/')
        sh.copy('Cards/me5_configuration.txt', signal.directory+'/Cards/')

def main():
    # mg5_path = '/extra/adarsh/Tools/mg5/'
    # do_parallel(lambda x: x.create_directory(mg5_path),signals)
    # do_parallel(copy_cards,signals)
    # parser = SafeConfigParser()
    # parser.read('config.ini')
    # do_parallel(lambda x: x.write_pbs_script(parser, 200), signals)
    map(lambda x: x.generate_events(), tqdm(signals, desc = "submitting PBS jobs"))

if __name__ == '__main__':
    main()
