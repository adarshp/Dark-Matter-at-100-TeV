#!/usr/bin/env python

from __future__ import division
import sys
import untangle
import multiprocessing as mp
sys.path.insert(0, '../clusterpheno')
from clusterpheno.helpers import cd, modify_file, do_parallel, convert_SAF_to_XML, get_SAF_objects
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

class BDTAnalysis(object):
    def __init__(self, signal):
        self.signal = signal
        self.signal_train_set, self.signal_test_set = get_signal_train_test_data(signal)
        self.tt_train_set, self.tt_test_set = get_bg_train_test_data('tt')
        
        X_train = pd.concat([self.signal_train_set, self.tt_train_set])
        X_test = pd.concat([self.signal_test_set, self.tt_test_set])

        y_train_signal = np.ones(self.signal_train_set.shape[0])
        y_train_bg = np.zeros(self.tt_train_set.shape[0])
        y_train = np.concatenate((y_train_signal, y_train_bg))

        clf = GradientBoostingClassifier(verbose = 3, loss = 'exponential')
        clf.fit(X_train, y_train)
        self.clf = clf

    def get_signal_train_test_data(signal):
        df = pd.read_csv(
            signal.directory+'/MakeFeatureArray/Output/feature_array.txt')
        return train_test_split(df)

    def get_bg_train_test_data(bg_name):
        df = pd.read_csv('BackgroundFeatureArrays/Output/{}/feature_array.txt'.format(bg_name))
        return train_test_split(df)

    def bdt_response_histo(self):
        d1 = self.clf.decision_function(self.signal_test_set)
        d2 = self.clf.decision_function(self.tt_test_set)
        matplotlib.style.use('ggplot')
        plt.hist(d1, bins = 40, color = 'DarkBlue')
        plt.hist(d2, bins = 40, color = 'Crimson')
        plt.savefig('bdt_response.pdf')
        plt.close()
    
        # def calculate_significance(self):
        # df = pd.DataFrame(index = ['Original','After preselection', 'After BDT cut'])

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

def get_xsection(signal):
    with open('Cards/prospino_output_xsections/{}_xsection.dat'.format(signal.index), 'r') as f:
        xs = float(f.readlines()[0].split()[-1:][0])
    xs = xs*1000.0 # Convert from ab to fb
    xs = xs*0.58 # Apply h->bb branching ratio
    xs = xs*0.067 # Apply Z-> ll branching ratio
    xs = xs*0.5 # Apply Goldstone equivalence theorem
    return xs

def calculate_significance(signal, bdt_cut):
    analysis = BDTAnalysis(signal)
    decisions = analysis.clf.decision_function(analysis.signal_test_set)
    passingevents = filter(lambda x: x > bdt_cut, decisions)
    xsection = get_xsection(signal)
    luminosity = 3000.
    nS = (len(passingevents)/len(decisions))*xsection*luminosity
    # nB = 

class Counter:
    def __init__(self, counter_object):
        cdata = counter_object.cdata.split('\n')
        self.name = cdata[1].split('\"')[1]
        self.nevents = int(cdata[2].split(' ')[0])

# def original_xsection(signal):
    # filepath = signal.directory+'/MakeFeatureArray/Output/Signal/Analysis/Cutflows/Signal'
    # n_orig = Counter((get_SAF_objects(filepath)).InitialCounter).nevents
    # print(n_orig)


def main():   
    # copy_analysis_shell_script(signals)
    # make_bdt_response_histo(signals[50])
    print(get_xsection(filter(lambda x: x.index == 'mH_1000_mB_525', signals)))

    
if __name__ == '__main__':
    main()
