#!/usr/bin/env python

import os
import shutil as sh
import myProcesses
from tqdm import tqdm
from DarkMatter.helpers import cd, modify_file
import subprocess as sp

def run_susyhit(signal):
    with cd('Tools/susyhit'):
        with open('suspect2_lha.in', 'w') as f:
            f.write(suspect_input_template.format(mH=str(signal.mH),
                    mB=str(signal.mB), mW=str(3000.),tb=str(10.0)))
        sp.call('./run', stdout = open(os.devnull, 'w'))
        sh.copy('slhaspectrum.in', '../../prospino_input/'+signal.name+'_slhaspectrum.in')
        sh.copy('susyhit_slha.out', '../../Cards/param_cards/'+signal.name+'_param_card.dat')

def run_prospino(signal, input_spectrum, prospino_directory,
                output_directory):

    """ Runs Prospino to get the Higgsino pair production cross section. """

    sh.copy(input_spectrum, prospino_directory+'/prospino.in.les_houches')

    with cd(prospino_directory):
        subprocess.call(['make', 'clean'], stdout = devnull)
        subprocess.call('make', stdout = devnull)
        subprocess.call('./prospino_2.run', stdout = devnull)

    sh.copy(prospino_directory+'/prospino.dat', 
            output_directory+'/'+signal.name+'_xsection.dat')

def create_mg5_directories():
    for signal in tqdm(myProcesses.signals[0:2]):
        signal.create_directory()
        sh.copy('Cards/delphes_cards/FCChh.tcl', 
                signal.directory+'/Cards/delphes_card.dat')
        sh.copy('Cards/run_cards/run_card.dat', 
                signal.directory+'/Cards/run_card.dat')
        sh.copy('Cards/param_cards/'+signal.name+'_param_card.dat', 
                signal.directory+'/Cards/param_card.dat')

# def run_susyhit(signal)
def main():   
    print(len(myProcesses.signals))

if __name__ == '__main__':
    main()
