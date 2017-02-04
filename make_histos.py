#!/usr/bin/env python

from __future__ import division
import sys
sys.path.insert(0,'/extra/adarsh/clusterpheno')
from clusterpheno.helpers import *
import matplotlib
matplotlib.use('Agg')
matplotlib.rc('text', usetex = True)
matplotlib.rc('xtick', labelsize = 11)
matplotlib.rc('ytick', labelsize = 11)
matplotlib.rc('font', size = 11)
from myProcesses import *
import matplotlib.pyplot as plt
figwidth = 3.06
plt.rcParams['figure.figsize'] = (figwidth,figwidth)
import itertools as it
import pandas as pd
import untangle
from BDTClassifier import BDTClassifier
import matplotlib.patches as mpatches

processes = ['Signal', 'tt', 'tbW',
            'bbWW',
            ]
colors = {'Signal': 'DarkBlue', 
          'tt': 'r',
          'tbW': 'green',
          'bbWW':'orange',
          }
ylabels = {'m_R': r'$\frac{1}{\sigma}\frac{d\sigma}{dM_R}$',
           'm_T_R': r'$\frac{1}{\sigma}\frac{d\sigma}{dM_T^R}$'}
xlabels = {'m_R': r'$M_R$ $\mathrm{(GeV)}$',
           'm_T_R': r'$M_T^R$ $\mathrm{(GeV)}$'}
patches = {}
for process in processes:
    patches[process] = mpatches.Rectangle((1,1),0.5,0.5, color = colors[process],
                                          label = r'${}$'.format(process), alpha = 0.4)
def make_histo(histo_name):

    for process_name in processes:
        with cd('CutAndCount/Output/'+process_name+'/Analysis_0/Histograms/'):
            convert_SAF_to_XML('histos.saf')
            objects = (untangle.parse('histos.xml')).root
            histos = objects.Histo
            myHisto = filter(lambda x: x.Description.cdata.split('\n')[1].strip('\"') == histo_name, histos)[0]
            nevents = int(myHisto.Statistics.cdata.split('\n')[1].split()[0])
            nbins = int(myHisto.Description.cdata.split('\n')[3].split()[0])
            xmin = float(myHisto.Description.cdata.split('\n')[3].split()[1])
            xmax = float(myHisto.Description.cdata.split('\n')[3].split()[2])
            bin_contents = [int(x.split()[0])/nevents for x in myHisto.Data.cdata.split('\n')[2:-2]]
            index = [x*(xmax-xmin)/nbins for x in range(1, nbins+1)]
            plt.style.use('ggplot')
            plt.bar(index, bin_contents, width = (xmax - xmin)/nbins, alpha = 0.4,
                    color = colors[process_name],
                    label = r'${}$'.format(process_name))
            plt.xlim(xmin, xmax)

def make_mTR_histo():
    make_histo('mTR')
    plt.ylabel(ylabels['m_T_R'], fontsize = 11)
    plt.xlabel(xlabels['m_T_R'], fontsize = 11)
    plt.ylim(0, 0.3)
    plt.legend(handles = [patches[process] for process in processes], fontsize = 10)
    axes = plt.axes()
    plt.locator_params(nbins = 6)
    axes.tick_params(axis = 'x', labelsize = 11)
    axes.tick_params(axis = 'y', labelsize = 11)
    axes.xaxis.set_label_coords(0.5, -0.20)
    plt.tight_layout()
    plt.savefig('images/mTR.pdf', dpi = 300)
    plt.close()

def make_mR_histo():
    make_histo('m_R')
    plt.ylabel(ylabels['m_R'])
    plt.xlabel(xlabels['m_R'])
    plt.legend(handles = [patches[process] for process in processes], fontsize = 10)
    axes = plt.axes()
    plt.locator_params(nbins = 6)
    axes.xaxis.set_label_coords(0.5, -0.2)
    plt.ylim(0, 0.12)
    plt.tight_layout()
    plt.savefig('images/mR.pdf')
    plt.close()

def collect_bdt_responses(BDTClassifier):
    for process in processes:
        with open('intermediate_results/bdt_responses/'+process+'.txt', 'w') as f:
            responses = BDTClassifier.clf.decision_function(BDTClassifier.test_sets[process])
            f.write('\n'.join(map(lambda x: str(x), responses)))

def make_bdt_histo():
    matplotlib.style.use('ggplot')
    responses = {}
    for process in processes:
        with open('intermediate_results/bdt_responses/'+process+'.txt', 'r') as f:
            responses[process] = map(lambda x: float(x), f.readlines())

    def weights(array):
        return np.ones_like(array)/float(len(array))
    plt.hist(responses['Signal'], weights = weights(responses['Signal']), bins = 30,
             color = 'DarkBlue', alpha = 0.4, label = r'$Signal$')
    plt.hist(responses['tt'], weights = weights(responses['tt']), bins = 30,
             color = 'Crimson', alpha = 0.4, label = r'$tt$')
    plt.hist(responses['tbW'], weights = weights(responses['tbW']), bins = 30,
             color = 'Green', alpha = 0.4, label = r'$tbW$')
    plt.hist(responses['bbWW'], weights = weights(responses['bbWW']), bins = 30,
             color = 'orange', alpha = 0.4, label = r'$bbWW$')
    plt.xlim(-10, 11)
    plt.ylim(0,0.3)
    plt.ylabel(r'$\frac{1}{\sigma}\frac{d\sigma}{dx}$',fontsize = 11)
    plt.xlabel(r'$\mathrm{BDT}$ $\mathrm{Response}$',fontsize = 11)
    axes = plt.axes()
    plt.locator_params(nbins = 8)
    axes.xaxis.set_label_coords(0.5, -0.2)
    plt.legend(handles = [patches[process] for process in processes], fontsize = 11, loc = 'upper center')
    plt.tight_layout()
    plt.savefig('images/bdt_response.pdf')
    plt.close()

def main():
    if sys.argv[1] == '--mR':
        make_mR_histo()
    elif sys.argv[1] == '--mTR':
        make_mTR_histo()
    elif sys.argv[1] == '--collect_bdt_rep':
        mySignal = filter(lambda x: x.mH == 1000 and x.mB == 25,signals)[0]
        classifier = BDTClassifier(mySignal)
        collect_bdt_responses(classifier)
    elif sys.argv[1] == '--bdt':
        figwidth = 4
        plt.rcParams['figure.figsize'] = (figwidth,figwidth*3/4)
        make_bdt_histo()

if __name__ == '__main__':
    main()
