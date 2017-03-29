#!/usr/bin/env python

from __future__ import division
import os
import sys
sys.path.insert(0, '/extra/adarsh/clusterpheno')
from clusterpheno.helpers import *
import subprocess as sp
import shutil as sh
from myProcesses import signals, backgrounds
from glob import glob
from tqdm import tqdm
import numpy as np
import untangle
import pandas as pd
import gzip
from BDTClassifier import BDTClassifier
import itertools as it
import multiprocessing as mp

def razor_combinations():
    """ Generate razor variable combinations. """
    mRs = np.arange(0.0,4000.0,100.0)
    mTRs = np.arange(0.0,2000.0,100.0)
    return list(it.product(mRs,mTRs))

def get_cutflow_from_objects(objects,process_name):
    """ Get cut flow (list of integers) from SAF/XML objects. """
    n_original = int(objects.InitialCounter.cdata.split('\n')[2].split()[0])
    counters = objects.Counter
    labels = ['Original']+[counter.cdata.split('\n')[1].split('#')[0].strip().strip('\"') for counter in counters]
    nevents= [n_original]+[int(counter.cdata.split('\n')[2].split()[0]) for counter in counters]
    df = pd.DataFrame(index = labels)
    df[process_name] = nevents
    return df

def get_original_bg_cutflow(bg_name):
    """ Get cutflow for backgrounds (unskimmed) """
    with cd('Preselection/Output/'+bg_name+'/Analysis_0/Cutflows'):
        convert_SAF_to_XML('Signal.saf')
        objects = untangle.parse('Signal.xml').root
    df = get_cutflow_from_objects(objects,bg_name)
    return df

def get_original_signal_cutflow(signal):
    """ Get original signal cutflow for a certain mass and razor var combination."""
    with cd ('Preselection/Output/'+signal.index+'/Analysis_0/Cutflows'):
        convert_SAF_to_XML('Signal.saf')
        objects = untangle.parse('Signal.xml').root
    df = get_cutflow_from_objects(objects,signal.index)
    return df

def get_skimmed_signal_cutflow(signal, razor_combo):
    razor_combo = str(int(razor_combo[0]))+'_'+str(int(razor_combo[1]))
    with cd('CutAndCount/Output/'+signal.index+'/'+razor_combo+'_skimmed/Cutflows'):
        convert_SAF_to_XML('Signal.saf')
        objects = untangle.parse('Signal.xml').root
    df = get_cutflow_from_objects(objects,signal.index)
    return df

def get_skimmed_bg_cutflow(bg_name, razor_combo):
    razor_combo = str(int(razor_combo[0]))+'_'+str(int(razor_combo[1]))
    with cd('CutAndCount/Output/'+bg_name+'/'+razor_combo+'_skimmed/Cutflows'):
        convert_SAF_to_XML('Signal.saf')
        objects = untangle.parse('Signal.xml').root
    df = get_cutflow_from_objects(objects,bg_name)
    return df

def substitute_bg_razor_cutflow_rows(bg_name, razor_combo):
    """ Substitute the last two rows of the unskimmed background event flow\
    with the last two rows of the skimmed background cutflow for a certain\
    razor variable. """
    df_original = get_original_bg_cutflow(bg_name)
    df_skimmed = get_skimmed_bg_cutflow(bg_name, razor_combo)
    df_new = pd.concat([df_original, df_skimmed[-2:]],axis=0,join='outer')
    return df_new

def substitute_signal_razor_cutflow_rows(signal, razor_combo):
    """ Substitute the last two rows of the unskimmed background event flow\
    with the last two rows of the skimmed background cutflow for a certain\
    razor variable. """
    df_original = get_original_signal_cutflow(signal)
    df_skimmed = get_skimmed_signal_cutflow(signal, razor_combo)
    df_new = pd.concat([df_original, df_skimmed[-2:]],axis=0,join='outer')
    return df_new

def make_cut_and_count_cut_flow_tables(mySignal, razor_combo, to_print=False):
    pd.set_option('precision',5)
    signal_df = substitute_signal_razor_cutflow_rows(mySignal, razor_combo) 
    bg_dfs = [substitute_bg_razor_cutflow_rows(bg_name, razor_combo) for bg_name in ['tt','tbW','bbWW']]
    dflist = [signal_df]+bg_dfs
    mc_events_df = pd.concat(dflist, axis = 1)
    mc_events_df['tt'] = map(lambda x: max(x, 3), mc_events_df['tt'])
    mc_events_df['tbW'] = map(lambda x: max(x, 3), mc_events_df['tbW'])
    mc_events_df['bbWW'] = map(lambda x: max(x, 3), mc_events_df['bbWW'])
    # print(mc_events_df)

    with open('tables/mc_events_table.tex', 'w') as f:
        mc_events_df.to_latex(f, escape=False)

    xs_df = mc_events_df
    xs_df[mySignal.index] = (xs_df[mySignal.index]/xs_df[mySignal.index][0])*mySignal.get_xsection()
    bg_xsections_df = pd.read_csv('bg_xsections.txt')

    with open('bg_xsections.txt', 'r') as f:
        lines = [line.strip() for line in f.readlines()]
        tt_xs = float(lines[0].split(',')[1])*1000
        tbW_xs = float(lines[1].split(',')[1])*1000
        bbWW_xs = float(lines[2].split(',')[1])*1000

    xs_df['tt'] = (xs_df['tt']/xs_df['tt'][0])*tt_xs
    xs_df['tbW'] = (xs_df['tbW']/xs_df['tbW'][0])*tbW_xs
    xs_df['bbWW'] = (xs_df['bbWW']/xs_df['bbWW'][0])*bbWW_xs

    nevents_df = xs_df*3000
    nevents_df['bg_tot'] = nevents_df['tt']+nevents_df['tbW']+nevents_df['bbWW']
    nevents_df['S/B'] = nevents_df[mySignal.index]/nevents_df['bg_tot']
    nevents_df['Significance'] = nevents_df[mySignal.index]/np.sqrt(nevents_df['bg_tot'])

    xs_df['bg_tot'] = xs_df['tt']+xs_df['tbW']+xs_df['bbWW']
    xs_df['S/B'] = nevents_df['S/B']
    xs_df['Significance'] = nevents_df['Significance']
    # print(xs_df)

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
    xs_df.columns = ['$\sigma_{signal}$',
                     '$\sigma_{tt}$',
                     '$\sigma_{tbW}$',
                     '$\sigma_{bbWW}$',
                     '$\sigma_{tot, BG}$',
                     '$S/B$',
                     '$S/\sqrt{B}$']

    xs_df = xs_df.loc[myrows]
    xs_df.index = ['Original',
                   'Trigger',
                   'SFOS leptons',
                   '2 $b$ jets',
                   '$MET < 400$',
                   '$85 < m_{ll} < 95$',
                   '$75 < m_{bb} < 150$',
                   '$m_{R} > 800$',
                   '$m_{T}^{R} > 400$'
                  ]

    def myFormatter(x):
        if x < 0.001:  return '%.1e' % x
        if x < 0.01:  return '%.3f' % x
        if x < 1: return '%.2f' % x
        if x < 10: return '%.1f' % x
        else: return "{:,.0f}".format(x)

    if to_print == True:
        with open('tables/cutflowtable.tex', 'w') as f:
            xs_df.to_latex(f,escape=False,float_format=myFormatter)
        with open('tables/3attobarns_events_table.tex', 'w') as f:
            nevents_df.to_latex(f, escape=False)

    return xs_df

def get_significance(signal, razor_combo):
    df = make_cut_and_count_cut_flow_tables(signal, razor_combo)
    nevents_after_cuts = df['$\sigma_{signal}$']['$m_{T}^{R} > 400$']*3000.
    if nevents_after_cuts < 5:
        return 0
    else:
        sig = df['$S/\sqrt{B}$'][-1]
        return sig

def get_max_significance(signal):
    max_sig = max([get_significance(signal, razor_combo) for razor_combo in tqdm(razor_combinations())])
    with open('intermediate_results/cc_scan_results/'+signal.index,'w') as f:
        f.write(','.join([str(signal.mH), str(signal.mB), str(max_sig)]))

def collect_max_sigs():
    with open('intermediate_results/cc_max_sigs.txt','w') as f:
        f.write('mH,mB,Significance\n')
        for signal in tqdm(signals):
            with open('intermediate_results/cc_scan_results/'+signal.index, 'r') as g:
                line = g.readline()+'\n'
                f.write(line)

if __name__ == '__main__':
    if sys.argv[1] == '--parallel':
        do_parallel(get_max_significance, signals, 28)
    elif sys.argv[1] == '--reduce':
        collect_max_sigs()
    elif sys.argv[1] == '--cc_rep':
        mySignal = filter(lambda x: x.mH == 1000 and x.mB == 25, signals)[0]
        make_cut_and_count_cut_flow_tables(mySignal,(800.0, 400.0),True)
