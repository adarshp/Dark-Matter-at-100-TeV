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
from glob import glob

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
 
class BDTClassifier(object):
    def __init__(self, signal):
        self.signal = signal
        self.train_sets = {}
        self.test_sets = {}
        bgs = ['tt', 'tbW', 'bbWW']
        self.get_signal_train_test_data()
        [self.get_bg_train_test_data(bg) for bg in bgs]

        bg_train_sets = [self.train_sets[bg_name] for bg_name in bgs]
        bg_test_sets = [self.test_sets[bg_name] for bg_name in bgs]

        X_train = pd.concat([self.train_sets['Signal']]+bg_train_sets)
        X_test = pd.concat([self.test_sets['Signal']]+bg_test_sets)

        y_train_signal = [np.ones(self.train_sets['Signal'].shape[0])]
        y_train_bgs = [np.zeros(self.train_sets[bg].shape[0]) for bg in bgs]
        y_train = np.concatenate(tuple(y_train_signal+y_train_bgs))

        GradientBoostingClassifier()
        clf = GradientBoostingClassifier(verbose = 3, loss = 'exponential')
        clf.fit(X_train, y_train)
        self.clf = clf

    def get_signal_train_test_data(self):
        df = pd.read_csv(
            self.signal.directory+'/MakeFeatureArray/Output/feature_array.txt')
        self.train_sets['Signal'], self.test_sets['Signal'] = train_test_split(df)

    def get_bg_train_test_data(self, bg_name):
        df = pd.read_csv('BackgroundFeatureArrays/Output/{}/feature_array.txt'.format(bg_name))
        self.train_sets[bg_name], self.test_sets[bg_name] = train_test_split(df)

def make_bdt_response_histo(BDTClassifier):
    d1 = BDTClassifier.clf.decision_function(BDTClassifier.test_sets['Signal'])
    d2 = BDTClassifier.clf.decision_function(BDTClassifier.test_sets['tt'])
    d3 = BDTClassifier.clf.decision_function(BDTClassifier.test_sets['tbW'])
    # d4 = BDTClassifier.clf.decision_function(BDTClassifier.test_sets['bbWW'])
    matplotlib.style.use('ggplot')
    plt.hist(d1, bins = 40, color = 'DarkBlue')
    plt.hist(d2, bins = 40, color = 'Crimson')
    plt.hist(d3, bins = 40, color = 'Green')
    plt.hist(d4, bins = 40, color = 'Orange')
    plt.savefig('bdt_response.pdf')
    plt.close()

def make_cut_flow_table(BDTClassifier, bdt_cut):
    df = pd.DataFrame(index  = ['Original', 
                                'After preselection',
                                'After BDT cut'])

    signal_decisions = BDTClassifier.clf.decision_function(BDTClassifier.test_sets['Signal'])
    decisions = {}
    decisions['tt'] = BDTClassifier.clf.decision_function(BDTClassifier.test_sets['tt'])
    decisions['tbW'] = BDTClassifier.clf.decision_function(BDTClassifier.test_sets['tbW'])
    # decisions['bbWW'] = BDTClassifier.clf.decision_function(BDTClassifier.test_sets['bbWW'])

    df['Signal'] = [BDTClassifier.signal.get_original_nevents(),
                    len(BDTClassifier.test_sets['Signal']),
                    len(filter(lambda x: x > bdt_cut, signal_decisions))]

    for bg in ['tt', 'tbW']: 
        df[bg] = [get_original_bg_events(bg),
                len(BDTClassifier.test_sets[bg]),
                len(filter(lambda x: x > bdt_cut, decisions[bg]))]

    df['Signal_xsection'] = (df['Signal']/df['Signal'][0])*signal.get_xsection()
    xsections = {}
    xsections['tt'] = 1850000.0
    xsections['tbW'] = 3230000.0
    xsections['bbWW'] = 24000.0

    bgs = ['tt', 'tbW']
    for bg in bgs:
        df[bg+'_xs'] = (df[bg]/df[bg][0])*xsections[bg]

    luminosity = 3000.
    df['Signal_events'] = df['Signal_xsection']*luminosity

    for bg in bgs:
        df[bg+'_events'] = df[bg+'_xs']*luminosity

    df['bg_events_tot'] = df['tt_events']+df['tbW_events']+df['bbWW_events']
    df['Significance'] = df['Signal_events']/np.sqrt(df['bg_events_tot'])

    # passingevents = filter(lambda x: x > bdt_cut, decisions)
    # xsection = get_xsection(signal)
    # luminosity = 3000.
    # nS = (len(passingevents)/len(decisions))*xsection*luminosity
    # nB =
    return df
def git_add():
    filelist = glob('Events/Signals/H1H2/bbll_MET/100_TeV/*/MakeFeatureArray/Output/feature_array.txt')
    for feature_array in tqdm(filelist):
        sp.call(['git', 'add', '-f', feature_array])

def main():
    # copy_analysis_shell_script(signals)
    # make_bdt_response_histo(signals[50])

    # do_parallel(lambda x: x.make_feature_array(), signals)
    # map(lambda x: x.make_feature_array(), signals)
    # print(make_cut_flow_table(signals[0], 0.))
    # myClassifier = BDTClassifier(signals[0])
    # print(make_cut_flow_table(myClassifier, 0.))
    # print(make_cut_flow_table(myClassifier, -1.))
    # print(make_cut_flow_table(myClassifier, 1.))

    git_add()
    
if __name__ == '__main__':
    main()
