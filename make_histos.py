#!/usr/bin/env python

from __future__ import division
import sys
sys.path.insert(0,'/extra/adarsh/clusterpheno')
from clusterpheno.helpers import *
import matplotlib
matplotlib.use('Agg')
matplotlib.rc('text', usetex = True)
matplotlib.rc('xtick', labelsize = 20)
matplotlib.rc('ytick', labelsize = 20)
matplotlib.rc('font', size = 20)
from myProcesses import *
import matplotlib.pyplot as plt
import itertools as it
import untangle
from BDTClassifier import BDTClassifier

colors = {'tt': 'r', 'Signal': 'DarkBlue', 'tbW': 'green'}
ylabels = {'m_R': r'$\frac{1}{\sigma}\frac{dM_R}{d\sigma}$',
           'm_T_R': r'$\frac{1}{\sigma}\frac{dM_T^R}{d\sigma}$'}
xlabels = {'m_R': r'$M_R$ $\mathrm(GeV)$',
           'm_T_R': r'$M_T^R$ $\mathrm(GeV)$'}

def make_histo(histo_name):

    for process_name in ['Signal','tt', 'tbW']:
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
                    label = process_name)
            plt.xlim(xmin, xmax)

def make_mTR_histo():
    make_histo('m_T_R')
    plt.ylabel(ylabels['m_T_R'], fontsize = 20)
    plt.xlabel(xlabels['m_T_R'], fontsize = 20)
    plt.text(1100, 0.35, r'$\mathcal{L} = 3000$ $\mathrm{fb}^{-1}$', fontsize = 20)
    plt.text(1100, 0.040, r'$\mathit{Signal}$', fontsize = 20, color = colors['Signal'])
    plt.text(250, 0.27, r'$tt$', fontsize = 20, color = colors['tt'])
    plt.text(325, 0.075, r'$tbW$', fontsize = 20, color = colors['tbW'])
    plt.ylim(0, 0.4)
    plt.tight_layout()
    plt.savefig('images/m_T_R.pdf', dpi = 300)
    plt.close()

def make_mR_histo():
    make_histo('m_R')
    plt.ylabel(ylabels['m_R'], fontsize = 20)
    plt.xlabel(xlabels['m_R'], fontsize = 20)
    plt.text(1400, 0.050, r'$\mathit{Signal}$', fontsize = 20)
    plt.text(700, 0.075, r'$tbW$', fontsize = 20)
    plt.text(600, 0.110, r'$tt$', fontsize = 20)
    plt.ylim(0, 0.2)
    plt.savefig('images/m_R.pdf')
    plt.close()

def make_bdt_response_histo(BDTClassifier):
    d1 = BDTClassifier.clf.decision_function(BDTClassifier.test_sets['Signal'])
    d2 = BDTClassifier.clf.decision_function(BDTClassifier.test_sets['tt'])
    d3 = BDTClassifier.clf.decision_function(BDTClassifier.test_sets['tbW'])
    # d4 = BDTClassifier.clf.decision_function(BDTClassifier.test_sets['bbWW'])
    matplotlib.style.use('ggplot')
    plt.hist(d1, bins = 100, color = 'DarkBlue', normed = True, alpha = 0.4)
    plt.hist(d2, bins = 100, color = 'Crimson', normed = True, alpha = 0.4)
    plt.hist(d3, bins = 100, color = 'Green', normed = True, alpha = 0.4)
    # plt.hist(d4, bins = 40, color = 'Orange', normed = True)
    plt.xlim(-10, 10)
    plt.savefig('images/bdt_response.pdf')
    plt.close()

def main():
    if sys.argv[1] == '--mR':
        make_mR_histo()
    elif sys.argv[1] == '--mTR':
        make_mTR_histo()
    elif sys.argv[1] == '--bdt':
        mySignal = filter(lambda x: x.mH == 1000 and x.mB == 25,signals)[0]
        classifier = BDTClassifier(mySignal)
        make_bdt_response_histo(classifier)

if __name__ == '__main__':
    main()
