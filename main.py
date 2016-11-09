#!/usr/bin/env python

from __future__ import division
import sys
import multiprocessing as mp
sys.path.insert(0, '../clusterpheno')
from clusterpheno.helpers import *
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


def get_original_bg_events(bg_name):
    filepath = 'BackgroundFeatureArrays/Output/{}/Analysis/Cutflows/Signal'.format(bg_name)
    return Counter((get_SAF_objects(filepath)).InitialCounter).nevents

def make_cut_flow_table(signal, bdt_cut):
    df = pd.DataFrame(index  = ['Original', 'After preselection',
                                'After BDT cut'])
    analysis = BDTAnalysis(signal)
    signal_decisions = analysis.clf.decision_function(analysis.signal_test_set)
    tt_decisions = analysis.clf.decision_function(analysis.tt_test_set)

    df['Signal'] = [signal.get_original_nevents(),
                    len(analysis.signal_test_set),
                    len(filter(lambda x: x > bdt_cut, signal_decisions))]

    df['tt'] = [get_original_bg_events('tt'),
                len(analysis.tt_test_set),
                len(filter(lambda x: x > bdt_cut,tt_decisions))]

    df['Signal_xsection'] = (df['Signal']/df['Signal'][0])*signal.get_xsection()
    df['tt_xs'] = (df['tt']/df['tt'][0])*1850000.0

    luminosity = 3000.
    df['Signal_events'] = df['Signal_xsection']*luminosity
    df['tt_events'] = df['tt_xs']*luminosity
    df['Significance'] = df['Signal_events']/df['tt_events']
    # passingevents = filter(lambda x: x > bdt_cut, decisions)
    # xsection = get_xsection(signal)
    # luminosity = 3000.
    # nS = (len(passingevents)/len(decisions))*xsection*luminosity
    # nB =
    return df

class BDTAnalysis(object):
    def __init__(self, signal):
        self.signal = signal
        self.get_signal_train_test_data()
        self.get_bg_train_test_data('tt')
        X_train = pd.concat([self.signal_train_set, self.tt_train_set])
        X_test = pd.concat([self.signal_test_set, self.tt_test_set])

        y_train_signal = np.ones(self.signal_train_set.shape[0])
        y_train_bg = np.zeros(self.tt_train_set.shape[0])
        y_train = np.concatenate((y_train_signal, y_train_bg))

        GradientBoostingClassifier()
        clf = GradientBoostingClassifier(verbose = 3, loss = 'exponential', n_estimators=300)
        clf.fit(X_train, y_train)
        self.clf = clf

    def get_signal_train_test_data(self):
        df = pd.read_csv(
            self.signal.directory+'/MakeFeatureArray/Output/feature_array.txt')
        self.signal_train_set, self.signal_test_set = train_test_split(df)

    def get_bg_train_test_data(self, bg_name):
        df = pd.read_csv('BackgroundFeatureArrays/Output/{}/feature_array.txt'.format(bg_name))
        self.tt_train_set, self.tt_test_set = train_test_split(df)

    def bdt_response_histo(self):
        d1 = self.clf.decision_function(self.signal_test_set)
        d2 = self.clf.decision_function(self.tt_test_set)
        matplotlib.style.use('ggplot')
        plt.hist(d1, bins = 40, color = 'DarkBlue')
        plt.hist(d2, bins = 40, color = 'Crimson')
        plt.savefig('bdt_response.pdf')
        plt.close()

def calculate_significance(signal, bdt_cut):
    analysis = BDTAnalysis(signal)
    decisions = analysis.clf.decision_function(analysis.signal_test_set)
    passingevents = filter(lambda x: x > bdt_cut, decisions)
    xsection = get_xsection(signal)
    luminosity = 3000.
    nS = (len(passingevents)/len(decisions))*xsection*luminosity

def main():
    # copy_analysis_shell_script(signals)
    # make_bdt_response_histo(signals[50])

    print(make_cut_flow_table(signals[0], -2.))

    
if __name__ == '__main__':
    main()
