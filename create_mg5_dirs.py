#!/usr/bin/env python

import os
import shutil as sh
import myProcesses
from tqdm import tqdm
from DarkMatter.helpers import cd, modify_file
import subprocess as sp

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
