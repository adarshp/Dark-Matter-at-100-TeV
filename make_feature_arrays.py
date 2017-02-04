#!/usr/bin/env python

from __future__ import division
import os
import sys
sys.path.insert(0, '/extra/adarsh/clusterpheno')
from clusterpheno.helpers import *
import subprocess as sp
import shutil as sh
from myProcesses import signals, backgrounds
from tqdm import tqdm
import pandas as pd
import numpy as np
from glob import glob
from BDTClassifier import BDTClassifier

def make_signal_feature_arrays():
    for signal in tqdm(signals):
        directory = signal.directory+'/MakeFeatureArray/Build/'
        sp.call(['cp','BackgroundFeatureArrays/Build/SampleAnalyzer/User/Analyzer/Analysis.cpp',
             directory+'SampleAnalyzer/User/Analyzer/'])
        scriptName = signal.index+'.pbs'
        with open(scriptName,'w') as f:
            f.write('''\
#!/bin/bash
#PBS -M adarsh@email.arizona.edu
#PBS -W group_list=shufang
#PBS -N {proc_name}
#PBS -q standard
#PBS -l jobtype=serial
#PBS -l select=1:ncpus=1:mem=2gb
#PBS -l place=pack:shared
#PBS -l cput=5:0:0
#PBS -l walltime=5:0:0
module load root
date
cd /xdisk/adarsh/Dark-Matter-at-100-TeV/{directory}
source setup.sh
make
rm -rf ../Output/*
./analyze.sh
date
exit 0
'''.format(directory = directory, proc_name = signal.index))
        sp.call(['qsub',scriptName],stdout=open(os.devnull,'w'))
        os.remove(scriptName)

def main():
    if sys.argv[1] == '--signals':
        make_signal_feature_arrays()

if __name__ == '__main__':
    main()
