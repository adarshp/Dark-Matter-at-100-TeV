#!/usr/bin/env python

from __future__ import division
import os
import time
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

def get_data(mySignal, process_name):
    """ Get event flow from SAF output"""
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

def get_xsection(filename):
    """ Get matched cross section from a .lhco.gz file"""
    with gzip.open(filename, 'r') as f:
        lines = f.readlines()
        myline = [line for line in lines if 'Matched Integrated weight' in line][0]
        print(filename)
        return float(myline.split()[-1])

def get_bg_xsection(bg_name):
    """ Collect cross sections from multiple .lhco.gz files and average them."""
    filenames = glob.glob('/extra/adarsh/Events/Backgrounds/'+bg_name+'/bbllvv/100_TeV/*/Events/*/*.lhco.gz')
    mean_xsection = np.mean(map(get_xsection, tqdm(filenames, desc = 'getting xsections for '+bg_name, dynamic_ncols=True)))
    with open('bg_xsections.txt', 'a') as f:
        f.write(bg_name+','+str(mean_xsection)+'\n')

def get_original_bg_events(bg_name):
    # filepath = 'BackgroundFeatureArrays/Output/{}/Analysis/Cutflows/Signal'.format(bg_name)
    filepath = 'MakeFeatureArrays/Output/{}/Analysis_0/Cutflows/Signal'.format(bg_name)
    return Counter((get_SAF_objects(filepath)).InitialCounter).nevents

def make_bdt_cut_flow_table(BDTClassifier, bdt_cut):
    df = pd.DataFrame(index  = ['After preselection',
                                'After BDT cut'])

    decisions = {}
    for process in ['Signal','tt', 'tbW', 'bbWW']:
        decisions[process] = BDTClassifier.clf.decision_function(BDTClassifier.test_sets[process])

    def feature_array_length(process_name):
        return len(BDTClassifier.train_sets[process_name]+BDTClassifier.test_sets[process_name])

    for process_name in ['Signal', 'tt', 'tbW', 'bbWW']:
        df[process_name] = [len(decisions[process_name]),
                            len(filter(lambda x: x > bdt_cut,decisions[process_name]))]

    signal_filepath = 'MakeFeatureArrays/Output/'+BDTClassifier.signal.index+'/Analysis_0/Cutflows/Signal'
    # signal_filepath = BDTClassifier.signal.directory+'/MakeFeatureArray/Output/Signal/Analysis/Cutflows/Signal'
    original_signal_events = Counter((get_SAF_objects(signal_filepath)).InitialCounter).nevents

    def fraction_after_preselection(process_name):
        if process_name == 'Signal':
            return feature_array_length(process_name)/original_signal_events
        else:
            return feature_array_length(process_name)/get_original_bg_events(process_name)

    signal_xsection = BDTClassifier.signal.get_xsection()*fraction_after_preselection('Signal')

    df['Signal_xs'] = (df['Signal']/df['Signal'][0])*signal_xsection

    xsections = {}
    with open('bg_xsections.txt', 'r') as f:
        lines = [line.strip() for line in f.readlines()]
        tt_xs = float(lines[0].split(',')[1])*1000
        tbW_xs = float(lines[1].split(',')[1])*1000
        bbWW_xs = float(lines[2].split(',')[1])*1000

    xsections['tt'] =  tt_xs*fraction_after_preselection('tt')
    xsections['tbW'] =  tbW_xs*fraction_after_preselection('tbW')
    xsections['bbWW'] =  bbWW_xs*fraction_after_preselection('bbWW')

    for bg in ['tt','tbW','bbWW']:
        df[bg+'_xs'] = ((df[bg]+3)/df[bg][0])*xsections[bg]

    df['bg_xs_total'] = df['tt_xs']+df['tbW_xs']+df['bbWW_xs']

    luminosity = 3000.

    for process_name in ['Signal', 'tt', 'tbW', 'bbWW']:
        df[process_name+'_events'] = df[process_name+'_xs']*luminosity

    df['bg_events_tot'] = df['tt_events']+df['tbW_events']+df['bbWW_events']
    df['$S/B$'] = df['Signal_events']/df['bg_events_tot']
    df['Significance'] = df['Signal_events']/np.sqrt(df['bg_events_tot'])

    with open('tables/paper_bdt_cutflowtable.tex', 'w') as f:
        df_paper = df[['Signal_xs','tt_xs','tbW_xs','bbWW_xs','bg_xs_total','$S/B$','Significance']]
        S = BDTClassifier.signal.get_xsection()
        B = sum([tt_xs,tbW_xs,bbWW_xs])
        df_paper.columns = ['$\sigma_{signal}$','$\signal_{tt}$','$\sigma_{tbW}$','$\sigma_{bbWW}$','$\sigma_{tot,BG}$','$S/B$','$S/\sqrt{B}$']
        df_paper.loc['Original'] = [S,tt_xs,tbW_xs,bbWW_xs,B,S/B,S*np.sqrt(luminosity/B)]
        df_paper.reindex(['Original','After preselection','After BDT cut'])
        def myFormatter(x):
            if x < 0.001: return '%.1e' % x
            if x < 0.01: return '%.3f' % x
            if x < 1: return '%.2f' % x
            if x < 10: return '%.1f' % x
            else: return '{:,.0f}'.format(x)
        df_paper.to_latex(f,escape=False,float_format = myFormatter)
    return df

def get_significance(classifier, bdt_cut):
    table = make_bdt_cut_flow_table(classifier, bdt_cut)
    sig = table['Significance'][-1]
    return sig

# BDT cut range to scan across
bdt_cut_range = tqdm(np.arange(0.0,15.0,0.1))

def run_bdt_test(signal):
    """ Run BDT test for a signal mass combination. """
    classifier = BDTClassifier(signal)
    print(max(map(lambda x: get_significance(classifier, x),bdt_cut_range)))
    # scores = cross_val_score(classifier.clf,
        # classifier.X_test, classifier.y_test, n_jobs = 2, cv = 10)
    # print(scores.mean(), scores.std()*2)

def write_nevents_to_file(signal):
    """ Scan over a range of bdt cuts and write the results to a file. """
    try:
        classifier = BDTClassifier(signal)
        # with open(signal.directory+'/MakeFeatureArray/nevents.csv', 'w') as f:
        with open('MakeFeatureArrays/Output/'+signal.index+'/nevents.csv', 'w') as f:
            print('ok so far')
            f.write('bdt_cut,nS,nB,significance\n')
            for bdt_cut in bdt_cut_range:
                table = make_bdt_cut_flow_table(classifier, bdt_cut)
                nS = table['Signal_events'][-1]
                nB = table['bg_events_tot'][-1]
                sig = table['Significance'][-1]
                f.write('{},{},{},{}\n'.format(str(bdt_cut),
                        str(int(nS)), str(int(nB)), str(sig)))
                                              
    except:
        pass

def write_submit_script(signal):
    with open('bdt_analysis_'+signal.index+'.pbs', 'w') as f:
        f.write('''\
#!/bin/bash
#PBS -N {mH}_{mB}
#PBS -M adarsh@email.arizona.edu
#PBS -W group_list=shufang
#PBS -q standard
#PBS -l select=1:ncpus=1:mem=6gb:pcmem=6gb
#PBS -l place=free:shared
#PBS -l cput=0:10:0
#PBS -l walltime=0:1:0
cd /xdisk/adarsh/Dark-Matter-at-100-TeV
date
./make_cutflowtable.py --bdt {mH} {mB}
date
'''.format(mH =str(int(signal.mH)), mB =str(int(signal.mB))))
    sp.call(['qsub', 'bdt_analysis_'+signal.index+'.pbs'], stdout = open(os.devnull,'w'))
    sp.call(['rm', 'bdt_analysis_'+signal.index+'.pbs'], stdout = open(os.devnull,'w'))

def main():
    if sys.argv[1] == '-h' or sys.argv[1] == '--help':
        print('''\
OPTIONS
--bdt_rep: Create a representative bdt cut flow table for mH = 1 TeV, mB = 25 GeV
--bdt mH mB: Make a BDT cut flow table for higgsino mass mH and bino mass mB
--cluster: Submit a number of jobs to the cluster, one for each mass combination
--interactive: Run BDT analyses on all mass combinations (but using one core)
--parallel: Run BDT analyses on all mass combinations (using 28 cpus on one Ocelote node)
''')
    elif sys.argv[1] == '--bdt_rep':
        # scores = cross_val_score(classifier.clf, classifier.X_test, classifier.y_test, n_jobs = -1, cv = 10)
        # print(scores.mean(), scores.std()*2)
        mySignal = filter(lambda x: x.mH == 1000 and x.mB == 25,signals)[0]
        classifier = BDTClassifier(mySignal)
        print make_bdt_cut_flow_table(classifier, 5.1)
    elif sys.argv[1] == '--bdt':
        mH = sys.argv[2]; mB = sys.argv[3]
        mySignal = filter(lambda x: x.mH == int(mH) and x.mB == int(mB),signals)[0]
        write_nevents_to_file(mySignal)
    elif sys.argv[1] == '--cluster':
        do_parallel(write_submit_script, signals)
    elif sys.argv[1] == '--interactive':
        for signal in tqdm(signals):
            write_nevents_to_file(signal)
    elif sys.argv[1] == '--parallel':
        do_parallel(write_nevents_to_file, signals, 14)
if __name__ == '__main__':
    main()
