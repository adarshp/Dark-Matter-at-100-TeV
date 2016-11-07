#!/usr/bin/env python

from __future__ import division
import sys
import multiprocessing as mp
sys.path.insert(0, '../clusterpheno')
from clusterpheno.helpers import cd, modify_file, do_parallel
import subprocess as sp
import shutil as sh
import os
from myProcesses import signals, backgrounds
from tqdm import tqdm
from ConfigParser import SafeConfigParser
from sklearn.cross_validation import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def create_template_analysis(parser):
    sp.call(['./'+parser.get('Tools', 'relative_ma5_path')+'/bin/ma5', '-E',
             'MakeFeatureArray', 'Analysis'])

def submit_signal_jobs():
    for process in tqdm(signals, dynamic_ncols = True,
                        desc = "submitting PBS jobs"):
        process.generate_events()

def make_feature_array(signal):
    with cd(signal.directory+'/MakeFeatureArray/Build'):
        devnull = open(os.devnull, 'w')
        sp.call('./analyze.sh', shell = True,
                stdout = devnull)

def copy_analysis_dir(signal):
    sh.rmtree(signal.directory+'/MakeFeatureArray')
    sh.copytree('MakeFeatureArray', signal.directory+'/MakeFeatureArray')

def get_signal_train_test_data(signal):
    df = pd.read_csv(
        signal.directory+'/MakeFeatureArray/Output/feature_array.txt')
    return train_test_split(df)

def get_bg_train_test_data(bg_name):
    df = pd.read_csv('BackgroundFeatureArrays/Output/{}/feature_array.txt'.format(bg_name))
    return train_test_split(df)

def get_trained_classifier(signal):
    signal_train_set, signal_test_set = get_signal_train_test_data(signal)
    tt_train_set, tt_test_set = get_bg_train_test_data('tt')
    
    X_train = pd.concat([signal_train_set, tt_train_set])
    X_test = pd.concat([signal_test_set, tt_test_set])

    y_train_signal = np.ones(signal_train_set.shape[0])
    y_train_bg = np.zeros(tt_train_set.shape[0])
    y_train = np.concatenate((y_train_signal, y_train_bg))
    clf = GradientBoostingClassifier(verbose = 3, loss = 'exponential')
    clf.fit(X_train, y_train)
    return clf

def make_bdt_response_histo(signal):
    clf = get_trained_classifier(signal)
    d1 = clf.decision_function(signal_test_set)
    d2 = clf.decision_function(tt_test_set)
    matplotlib.style.use('ggplot')
    plt.hist(d1, bins = 40, color = 'DarkBlue')
    plt.hist(d2, bins = 40, color = 'Crimson')
    plt.savefig('bdt_response.pdf')
    plt.close()

def run_prospino(signal):
    """ Runs Prospino to get the Higgsino pair production cross section. """

    input_spectrum = 'Cards/prospino_input/'+signal.index+'_slhaspectrum.in'
    sh.copy(input_spectrum, 'Tools/Prospino2/prospino.in.les_houches')

    with cd('Tools/Prospino2'):
        devnull = open(os.devnull, 'w')
        sp.call(['make', 'clean'], stdout = devnull, stderr = devnull)
        sp.call('make', stdout = devnull, stderr = devnull)
        sp.call('./prospino_2.run', stdout = devnull, stderr = devnull)
        sh.copy('prospino.dat', 
            '../../Cards/prospino_output_xsections/'+signal.index+'_xsection.dat')

def main():   
    # copy_analysis_shell_script(signals)
    # make_bdt_response_histo(signals[50])
    map(run_prospino, tqdm(signals[0:2]))

    
if __name__ == '__main__':
    main()
