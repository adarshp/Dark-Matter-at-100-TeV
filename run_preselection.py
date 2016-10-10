#!/usr/bin/env python

import os
from tqdm import tqdm
import subprocess as sp
from myProcesses import myProcesses
from helpers import cd, modify_file, razor_combinations
from CutAndCountAnalysis import CutAndCountAnalysis


def run_preselection():
   
    my_processes = myProcesses()
    signals = my_processes.signals

    mySignals = filter(lambda process: process.higgsino_mass > 2000, signals)

    backgrounds = my_processes.backgrounds

    devnull = open(os.devnull, 'w')

    analysis = CutAndCountAnalysis()
    analysis.write_analysis_cpp('Preselection', 0.0, 0.0)

    with cd('Preselection/Build'):
        sp.call('make', stdout = devnull, stderr = devnull)


    for process in tqdm(mySignals, ncols = 60, unit = 'Mass combinations'):
        process.make_original_input_list('Preselection')
        sp.call('rm -rf Preselection/Output/{}'.format(process.name), shell = True)
        process.analyze_originals('Preselection', 'PreselectionAnalysis')
        with cd('Preselection/Build/'):
            sp.call('mv -f *.lhco ../Output', shell = True, 
                        stdout = devnull, stderr = devnull) 
"""
    for process in tqdm(backgrounds, ncols = 60, desc = 'Skimming backgrounds'):
        tqdm.write('Skimming background '+process.name)
        process.make_original_input_list('Preselection')
        process.analyze_originals('Preselection', 'PreselectionAnalysis')
        with cd('Preselection/Build/'):
            sp.call('mv *.lhco ../Output', shell = True,
                        stdout = devnull, stderr = devnull) 
"""
def main():
    run_preselection()

if __name__ == '__main__':
    main()
