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
import numpy as np
import untangle
import pandas as pd
import gzip
import glob
from BDTClassifier import BDTClassifier
from sklearn.model_selection import cross_val_score
from make_bdt_histo import make_bdt_response_histo

def get_data(mySignal, process_name):
    with cd('CutAndCount/Output/'+process_name+'/Analysis_0/Cutflows'):
        convert_SAF_to_XML('Signal.saf')
        objects = untangle.parse('Signal.xml').root
    n_original = int(objects.InitialCounter.cdata.split('\n')[2].split()[0])
    counters = objects.Counter
    labels = ['Original']+[counter.cdata.split('\n')[1].split('#')[0].strip().strip('\"') for counter in counters]
    nevents = [n_original]+[int(counter.cdata.split('\n')[2].split()[0]) for counter in counters]
    df = pd.DataFrame(index = labels)
    df[process_name] = nevents
    return df

def make_cut_and_count_cut_flow_table():
    mySignal = filter(lambda x: x.mH == 1000 and x.mB == 25,signals)[0]
    dflist = map(lambda x: get_data(mySignal, x), ['Signal', 'tt', 'tbW'])
    pd.set_option('precision',2)

    mc_events_df = pd.concat(dflist, axis = 1)
    mc_events_df['tt'] = map(lambda x: max(x, 3), mc_events_df['tt'])
    mc_events_df['tbW'] = map(lambda x: max(x, 3), mc_events_df['tbW'])

    xs_df = mc_events_df
    xs_df['Signal'] = (xs_df['Signal']/xs_df['Signal'][0])*mySignal.get_xsection()
    xs_df['tt'] = (xs_df['tt']/xs_df['tt'][0])*36000
    xs_df['tbW'] = (xs_df['tbW']/xs_df['tbW'][0])*151000

    nevents_df = xs_df*3000
    nevents_df['bg_tot'] = nevents_df['tt']+nevents_df['tbW']
    nevents_df['S/B'] = nevents_df['Signal']/nevents_df['bg_tot']
    nevents_df['Significance'] = nevents_df['Signal']/np.sqrt(nevents_df['bg_tot'])

    xs_df['bg_tot'] = nevents_df['tt']+nevents_df['tbW']
    xs_df['S/B'] = nevents_df['S/B']
    xs_df['Significance'] = nevents_df['Significance']
    print(xs_df)

    myrows = ['Original',
              'Lepton trigger',
              'OS leptons',
              '2 b jets',
              'MET',
              'm_ll',
              'm_bb',
              'm_R',
              'mTR'
              ]
    xs_df.columns = ['$\sigma_{signal}$ (fb)',
                     '$\sigma_{tt}$ (fb)',
                     '$\sigma_{tbW}$ (fb)',
                     '$\sigma_{tot, BG} (fb)$',
                     '$S/B$',
                     '$S/\sqrt{B}$ (3 ab$^{-1})$']
    xs_df = xs_df.loc[myrows]

    xs_df.index = ['Original',
                   'Trigger',
                   'SFOS leptons',
                   '2 $b$ jets',
                   'MET',
                   '$m_{ll}$',
                   '$m_{bb}$',
                   '$m_{R}$',
                   '$m_{T}^{R}$'
                  ]
    f = open('tables/cutflowtable.tex', 'w')
    print(xs_df.to_latex(f,escape=False))
    f.close()

def get_xsection(filename):
    with gzip.open(filename, 'r') as f:
        lines = f.readlines()
        myline = [line for line in lines if 'Matched Integrated weight' in line][0]
        return float(myline.split()[-1])

def get_bg_xsection(bg_name):
    filenames = glob.glob('/extra/adarsh/Events/Backgrounds/'+bg_name+'/bbllvv/100_TeV/*/Events/*/*.lhco.gz')
    xsections = map(get_xsection, tqdm(filenames, desc = 'getting xsections for '+bg_name, dynamic_ncols=True))
    mean_xsection = sum(xsections)/len(xsections)
    with open('bg_xsections.txt', 'a') as f:
        f.write(bg_name+','+str(mean_xsection)+'\n')

def get_original_bg_events(bg_name):
    filepath = 'BackgroundFeatureArrays/Output/{}/Analysis/Cutflows/Signal'.format(bg_name)
    return Counter((get_SAF_objects(filepath)).InitialCounter).nevents

def make_bdt_cut_flow_table(BDTClassifier, bdt_cut):
    df = pd.DataFrame(index  = ['After preselection',
                                'After BDT cut'])

    decisions = {}
    decisions['tt'] = BDTClassifier.clf.decision_function(BDTClassifier.test_sets['tt'])
    decisions['tbW'] = BDTClassifier.clf.decision_function(BDTClassifier.test_sets['tbW'])
    decisions['Signal'] = BDTClassifier.clf.decision_function(BDTClassifier.test_sets['Signal'])

    # decisions['bbWW'] = BDTClassifier.clf.decision_function(BDTClassifier.test_sets['bbWW'])
    def feature_array_length(process_name):
        return len(BDTClassifier.train_sets[process_name]+BDTClassifier.test_sets[process_name])

    for process_name in ['Signal',
                         'tt',
                        'tbW'
                        ]:
        df[process_name] = [len(BDTClassifier.test_sets[process_name]),
                  len(filter(lambda x: x > bdt_cut, decisions[process_name]))]

    signal_filepath = 'Events/Signals/H1H2/bbll_MET/100_TeV/{}/'.format(BDTClassifier.signal.index)\
                        +'MakeFeatureArray/Output/Signal/Analysis/Cutflows/Signal'
    original_signal_events = Counter((get_SAF_objects(signal_filepath)).InitialCounter).nevents

    def fraction_after_preselection(process_name):
        if process_name == 'Signal':
            return feature_array_length(process_name)/original_signal_events
        else:
            return feature_array_length(process_name)/get_original_bg_events(process_name)

    signal_xsection = BDTClassifier.signal.get_xsection()*fraction_after_preselection('Signal')

    df['Signal_xs'] = (df['Signal']/df['Signal'][0])*signal_xsection

    xsections = {}
    xsections['tt'] =  36000.0*fraction_after_preselection('tt')
    xsections['tbW'] =  151000.0*fraction_after_preselection('tbW')
    # xsections['bbWW'] = 24000.0

    bgs = [
             'tt',
           'tbW',
           ]
    for bg in bgs:
        df[bg+'_xs'] = ((df[bg]+3)/df[bg][0])*xsections[bg]

    luminosity = 3000.
    df['Signal_events'] = df['Signal_xs']*luminosity

    for bg in bgs:
        df[bg+'_events'] = df[bg+'_xs']*luminosity

    df['bg_events_tot'] = df['tt_events']+df['tbW_events']#+df['bbWW_events']
    df['Significance'] = df['Signal_events']/np.sqrt(df['bg_events_tot'])

    return df

def write_nevents_to_file(classifier):
    def get_sig(bdt_cut):
        table = make_cut_flow_table(classifier, bdt_cut)
        nS = table['Signal_events'][-1]
        nB = table['bg_events_tot'][-1]
        string = '{},{},{},{}'.format(str(bdt_cut),
                                    str(int(nS)),
                                    str(int(nB)),
                                    str(nS/np.sqrt(nB)))
        return string

    with open(classifier.signal.directory+'/MakeFeatureArray/nevents.csv', 'w') as f:
        f.write('bdt_cut,nS,nB,significance\n')
        list_of_strings = '\n'.join(map(get_sig, tqdm(np.arange(0.0, 15.0, 0.1))))
        f.write(list_of_strings)

def main():
    if sys.argv[1] == '--bdt':
        mySignal = filter(lambda x: x.mH == 1000 and x.mB == 25,signals)[0]
        classifier = BDTClassifier(mySignal)
        make_bdt_response_histo(classifier)
        scores = cross_val_score(classifier.clf, classifier.X_test, classifier.y_test, n_jobs = -1, cv = 10)
        print(scores.mean(), scores.std()*2)
        write_nevents_to_file(classifier)
        print(make_cut_flow_table(classifier, 5.))
        make_bdt_cut_flow_table()
    else:
        make_cut_and_count_cut_flow_table()

if __name__ == '__main__':
    main()
