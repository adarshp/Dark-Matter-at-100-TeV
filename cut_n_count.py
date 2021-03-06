#!/usr/bin/env python

from __future__ import division
import os
import sys
sys.path.insert(0, '/extra/adarsh/clusterpheno')
from clusterpheno.helpers import *
import subprocess as sp
import shutil as sh
import itertools as it
from myProcesses import signals, backgrounds
from tqdm import tqdm
from ConfigParser import SafeConfigParser
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from glob import glob
import random
import multiprocessing as mp
from BDTClassifier import BDTClassifier
from sklearn.model_selection import train_test_split

def create_template_analysis(parser):
    sp.call(['./'+parser.get('Tools', 'relative_ma5_path')+'/bin/ma5', '-E',
             'MakeFeatureArray', 'Analysis'])

def preselect_signals():
    """ Run preselection on signals """
    with cd('Preselection/Build'):
        for signal in tqdm(signals,ncols=80):
            scriptName = signal.index+".pbs"
            with open(scriptName,'w') as f:
                f.write('''\
#!/bin/bash
#PBS -M adarsh@email.arizona.edu
#PBS -W group_list=shufang
#PBS -N {proc_name}
#PBS -q windfall
#PBS -l select=1:ncpus=1:mem=2gb
#PBS -l place=free:shared
#PBS -l cput=5:0:0
#PBS -l walltime=5:0:0
date
cd /rsgrps/shufang/Dark-Matter-at-100-TeV/Preselection/Build
source setup.sh
./analyze.sh {proc_name}
date
'''.format(proc_name = 'mH_'+str(int(signal.mH))+'_mB_'+str(int(signal.mB))))
            sp.call(['qsub',scriptName],stdout=open(os.devnull,'w'))
            os.remove(scriptName)

def make_skimmed_input_list(signal):
    """ Make input lists for skimmed LHCO files. """
    with open('CutAndCount/Input/Skimmed/'+signal.index, 'w') as f:
        f.write('../../Preselection/Output/Skimfiles/'+signal.index+'.lhco')

def make_skimmed_bg_input_list(bg):
    """ Make input lists for skimmed LHCO background files. """
    with open('CutAndCount/Input/Skimmed/'+bg, 'w') as f:
        f.write('../../Preselection/Output/Skimfiles/'+bg+'.lhco')

def set_razor_cuts(mR,mTR):
    """ Set razor cuts and compile. """
    def modfn(line):
        """ Line modification function to modify Analysis.cpp """
        if "mR >" in line:
            return "\tif(!Manager()->ApplyCut(mR > {}, \"m_R\")) return false;\n".format(str(mR))
        elif "mTR >" in line:
            return "\tif(!Manager()->ApplyCut(mTR > {}, \"mTR\")) return false;\n".format(str(mTR))
        else: 
            return line

    with cd('CutAndCount/Build'):
        modify_file('SampleAnalyzer/User/Analyzer/Analysis.cpp',modfn)
        sp.call('make',stdout = open(os.devnull,'w'))

def razor_combinations():
    """ Generate combinations of razor variables"""
    mRs = np.arange(0.0,4000.0,100.0)
    mTRs = np.arange(0.0,2000.0,100.0)
    return list(it.product(mRs,mTRs))

def analyze_signal_skimmed(signal,razor_combo):
    razor_combo = str(int(razor_combo[0]))+'_'+str(int(razor_combo[1]))
    with cd('CutAndCount/Build'):
        sp.call(['./MadAnalysis5job','../Input/Skimmed/'+signal.index],
                stdout=open(os.devnull,'w'),stderr=open(os.devnull,'w'))
        razor_dir = '../Output/'+signal.index+'/'+razor_combo+'_skimmed'
        sp.call(['rm','-rf', razor_dir])
        sp.call(['mv','../Output/'+signal.index+'/Analysis_0',
                 razor_dir])

def analyze_bg_skimmed(bg_name, razor_combo):
    """ Analyze skimmed background events. """
    razor_combo = str(int(razor_combo[0]))+'_'+str(int(razor_combo[1]))
    with cd('CutAndCount/Build'):
        sp.call(['./MadAnalysis5job','../Input/Skimmed/'+bg_name],
                stdout=open(os.devnull,'w'),stderr=open(os.devnull,'w'))
        razor_dir = '../Output/'+bg_name+'/'+razor_combo+'_skimmed'
        sp.call(['rm','-rf', razor_dir])
        sp.call(['mv','../Output/'+bg_name+'/Analysis_0', razor_dir])

def analyze_signals():
    razor_combos = razor_combinations()
    for combo in tqdm(razor_combos):
        set_razor_cuts(combo[0], combo[1])
        do_parallel(lambda x: analyze_signal_skimmed(x,combo), signals, 28)

def analyze_backgrounds(bgs):
    razor_combos = razor_combinations()
    for combo in tqdm(razor_combos):
        set_razor_cuts(combo[0], combo[1])
        do_parallel(lambda x: analyze_bg_skimmed(x,combo), bgs, 3)

def preselect_backgrounds():
    """ Run preselection for backgrounds (on login node) """
    bgs = ['tt_fully_leptonic','tbW_bbllvv','bbWW_bbllvv']
    with cd('Preselection/Build'):
        do_parallel(lambda x: sp.call(['./analyze_bgs.sh', x]), bgs, 3)
        
def main():
    if sys.argv[1] == '--preselect_signals':
        preselect_signals()
    if sys.argv[1] == '--preselect_backgrounds':
        preselect_backgrounds()
    if sys.argv[1] == '--analyze_signals':
        map(make_skimmed_input_list, tqdm(signals, ncols=80))
        analyze_signals()
    if sys.argv[1] == '--analyze_backgrounds':
        bgs = ['tt', 'tbW', 'bbWW']
        map(make_skimmed_bg_input_list, tqdm(bgs, ncols=80))
        analyze_backgrounds(bgs)

if __name__ == '__main__':
    main()
