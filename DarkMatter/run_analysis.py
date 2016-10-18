#!/usr/bin/env python

import os
from tqdm import tqdm
import subprocess as sp
from myProcesses import myProcesses
from helpers import cd, modify_file, razor_combinations
from CutAndCountAnalysis import CutAndCountAnalysis
import shutil as sh
import glob

my_processes = myProcesses()
signals = my_processes.signals
backgrounds = my_processes.backgrounds

def run_analysis_on_originals():

    analysis = CutAndCountAnalysis()
    m_R = 0.0; m_T_R = 0.0
    analysis.write_analysis_cpp('CutAndCountAnalysis', m_R, m_T_R)

    with cd('CutAndCountAnalysis/Build'):
        devnull = open(os.devnull, 'w')
        sp.call(['make']) 

    analysis_name = str(int(m_R))+'_GeV_m_R_'+str(int(m_T_R))+'_GeV_m_T_R'

    for process in tqdm(signals, ncols = 60):
        process.make_original_input_list('CutAndCountAnalysis')
        process.analyze_originals('CutAndCountAnalysis', analysis_name)

    """
    for process in tqdm(backgrounds, ncols = 60):
        process.make_original_input_list('CutAndCountAnalysis')
        process.analyze_originals('CutAndCountAnalysis', analysis_name)
        """

def main():
    run_analysis_on_originals()

if __name__ == '__main__':
    main()
