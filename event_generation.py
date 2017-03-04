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
        # sh.copy('Cards/delphes_cards/momentumResolutionVsP.tcl', signal.directory+'/Cards/')
        # sh.copy('Cards/delphes_cards/muonMomentumResolutionVsP.tcl', signal.directory+'/Cards/')
        sh.copy('Cards/me5_configuration.txt', signal.directory+'/Cards/')

def write_pbs_scripts(processes, parser, nruns):
    for process in tqdm(processes, dynamic_ncols = True,
                        desc = 'Writing PBS submit scripts'):
        with open(parser.get('PBS Templates', 'generate_script'), 'r') as f:
            string = f.read()
        with open(process.directory+'/generate_events.pbs', 'w') as f:
            f.write(string.format(jobname =process.index,
                                  username = parser.get('Cluster', 'username'),
                                  email = parser.get('Cluster', 'email'),
                                  group_list = parser.get('Cluster', 'group_list'),
                                  nruns = str(nruns),
                                  cput = str(28*nruns),
                                  walltime = str(1*nruns),
                                  cwd = os.getcwd(),
                                  mg5_process_dir = process.directory))

def main():
    # mg5_path = '/extra/adarsh/Tools/mg5/'
    # do_parallel(lambda x: x.create_directory(mg5_path),signals,28)
    # do_parallel(copy_cards,signals, 2)
    # parser = SafeConfigParser()
    # parser.read('config.ini')
    # write_pbs_scripts(signals, parser, 1)
    # do_parallel(lambda x: x.write_pbs_script(parser, 1), signals, 28)
    map(lambda x: x.generate_events(), tqdm(signals[0:2], desc = "submitting PBS jobs"))

if __name__ == '__main__':
    main()
