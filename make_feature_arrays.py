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
        scriptName = signal.index+'.pbs'
        with open(scriptName,'w') as f:
            f.write('''\
#!/bin/bash
#PBS -M adarsh@email.arizona.edu
#PBS -W group_list=shufang
#PBS -N {proc_name}
#PBS -q windfall
#PBS -l select=1:ncpus=1:mem=6gb:pcmem=6gb
#PBS -l place=free:shared
#PBS -l cput=5:0:0
#PBS -l walltime=5:0:0
date
cd /xdisk/adarsh/Dark-Matter-at-100-TeV/MakeFeatureArrays/Build
./analyze.sh {proc_name}
date
exit 0
'''.format(proc_name = signal.index))
        sp.call(['qsub',scriptName],stdout=open(os.devnull,'w'))
        os.remove(scriptName)

def data_cleaning(proc_name):
    header = 'ptl1,ptl2,ptb1,ptb2,mll,mbb,mllbb,mR,mTR,MET,THT\n'
    with open('MakeFeatureArrays/Output/'+proc_name+'/feature_array.txt','r+') as f:
        lines = f.readlines()
        if not lines[0].startswith('p'):
            f.seek(0)
            lines.insert(0,header)
            f.writelines(lines)
            f.truncate()

def main():
    if sys.argv[1] == '--signals':
        make_signal_feature_arrays()
    if sys.argv[1] == '--dc':
        bgs = ['tt','tbW','bbWW']
        signal_names = map(lambda x: x.index, signals)
        map(data_cleaning,tqdm(signal_names+bgs))

if __name__ == '__main__':
    main()
