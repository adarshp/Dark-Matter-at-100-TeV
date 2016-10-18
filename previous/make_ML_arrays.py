#!/usr/bin/env python

import os
from tqdm import tqdm
import subprocess as sp
from myProcesses import myProcesses
from helper_functions import cd, modify_file, razor_combinations
from MakeFeatureArray import MakeFeatureArray


def make_ML_arrays():
   
    my_processes = myProcesses()
    signals = my_processes.signals
    backgrounds = my_processes.backgrounds

    # mySignals = filter(lambda process: process.higgsino_mass > 2000, signals)

    dirname = 'Make_ML_Arrays'
    devnull = open(os.devnull, 'w')

    with cd(dirname+'/Build'):
        sp.call('make')

    analysis = MakeFeatureArray()
    analysis.write_analysis_cpp(dirname)

    for process in tqdm(signals, ncols = 60, unit = 'Mass combinations'):
        sp.call('rm -rf Make_ML_Arrays/Output/{}*'.format(process.name),
                shell = True) 
        process.make_original_input_list(dirname)
        process.analyze_originals(dirname, 'ML_Arrays')

def main():
    make_ML_arrays()

if __name__ == '__main__':
    main()
