#!/usr/bin/env python

import os
import subprocess as sp
from tqdm import tqdm
from myProcesses import myProcesses
from helpers import cd, modify_file, razor_combinations
from CutAndCountAnalysis import CutAndCountAnalysis
import glob

my_processes = myProcesses()
signals = my_processes.signals
backgrounds = my_processes.backgrounds

def run_skimmed_analysis(razor_combo):

    m_R = razor_combo[0]; m_T_R = razor_combo[1]

    analysis = CutAndCountAnalysis()
    analysis.write_analysis_cpp('CutAndCountAnalysis', m_R, m_T_R)

    with cd('CutAndCountAnalysis/Build'):
        devnull = open(os.devnull, 'w')
        sp.call('make', stdout = devnull, stderr = devnull)

    analysis_name = str(int(m_R))+'_GeV_m_R_'+str(int(m_T_R))+'_GeV_m_T_R'

    def analyze_processes(processes):
        for process in tqdm(processes, ncols = 80):
            sp.call(['rm','-rf', 
                'CutAndCountAnalysis/Output/'+process.name+'_skimmed/'+analysis_name])
            process.make_skimmed_input_list('CutAndCountAnalysis')
            process.analyze_skimmed('CutAndCountAnalysis', analysis_name)

    analyze_processes(signals)
    analyze_processes(backgrounds)

def main():

    print('Running skimmed analysis')

    for razor_combo in tqdm(razor_combinations(), ncols = 80,
                     unit ='Razor variable combination'):
        run_skimmed_analysis(razor_combo)

if __name__ == '__main__':
    main()
