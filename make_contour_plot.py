#!/usr/bin/env python

from __future__ import division
import os
import sys
sys.path.insert(0, '/extra/adarsh/clusterpheno')
from clusterpheno.helpers import *
from myProcesses import signals
import matplotlib
matplotlib.use('Agg')
matplotlib.rc('text', usetex = True)
matplotlib.rc('xtick', labelsize = 11)
matplotlib.rc('ytick', labelsize = 11)
matplotlib.rc('font', size = 11)
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

figwidth = 6.12
plt.rcParams['figure.figsize'] = (figwidth,figwidth*3/4)

def get_max_bdt_significance(signal):
    with cd(signal.directory+'/MakeFeatureArray/'):
        df = pd.read_csv('nevents.csv')
        return max(df['significance'])

def collect_max_bdt_sigs():
    with open('intermediate_results/bdt_sigs.txt', 'w') as f:
        f.write('mH,mB,Significance\n')
        for signal in tqdm(signals):
            f.write(','.join([str(signal.mH),
                              str(signal.mB),
                              str(get_max_bdt_significance(signal))])+'\n')

def get_XYZ_grid(df,res):
    df = df.replace('None',0)
    x = df['mH']
    y = df['mB']
    z = df['Significance']

    resX = res; resY = res
    xi = np.linspace(525, 2000, resX)
    yi = np.linspace(25, 1500, resY)
    X, Y = np.meshgrid(xi, yi)
    Z = matplotlib.mlab.griddata(x,y,z,xi,yi,interp='nn')
    return X,Y,Z

def make_line():
    x = np.arange(525,2500, 0.1) 
    plt.plot(x,x,color = 'gray', linestyle = 'dashed')

def set_axis_labels():
    plt.xlim(525,1600)
    plt.ylim(0,1200)
    plt.text(550, 1075, r"$\mathcal{L} = 3000$ $\mathrm{fb}^{-1}$", fontsize = 20)
    plt.text(700, 830, r"$M_1 = |\mu|$", fontsize = 11, rotation = 32)
    plt.ylabel(r'$M_1$ $\mathrm{(GeV)}$', fontsize = 11)
    plt.xlabel(r'$|\mu|$ $\mathrm{(GeV)}$', fontsize = 11)
    axes = plt.axes()
    axes.xaxis.set_label_coords(0.5, -0.1)
    axes.yaxis.set_label_coords(-0.08, 0.5)
    plt.tight_layout()

def make_contour_plot(levels, filename, res, colors):
    bdt_df = pd.read_csv('intermediate_results/bdt_sigs.txt')
    cc_df = pd.read_csv('intermediate_results/cc_max_sigs.txt')

    plt.style.use('ggplot')

    fmt = {}
    X, Y, Z = get_XYZ_grid(bdt_df,res)
    bdt_CS = plt.contour(X,Y,Z,levels = levels, linestyles = 'dashed', colors = colors)
    fmt[bdt_CS.levels[0]] = r'$\mathrm{BDT}$'
    plt.clabel(bdt_CS, inline=1, fontsize=11, fmt=fmt)
    X, Y, Z = get_XYZ_grid(cc_df,res)
    cc_CS = plt.contour(X,Y,Z,levels = levels, linestyles = 'solid', colors = colors)
    fmt[cc_CS.levels[0]] = '$\mathrm{CC}$'
    plt.clabel(cc_CS, inline=1, fontsize=11, fmt=fmt)

    make_line()
    set_axis_labels()
    plt.text(600, 1200, r"${}\sigma$".format(levels[0]), fontsize = 14)

    plt.tight_layout()
    plt.savefig('images/{}.pdf'.format(filename))

def make_combined_contour_plot():
    bdt_df = pd.read_csv('intermediate_results/bdt_sigs.txt')
    cc_df = pd.read_csv('intermediate_results/cc_max_sigs.txt')

    plt.style.use('ggplot')

    res = 100
    fmt = {}
    X, Y, Z = get_XYZ_grid(bdt_df,res)
    colors = ['DarkBlue','Maroon']
    bdt_CS = plt.contour(X,Y,Z,levels = [1.96,5], linestyles = 'dashed', colors = colors)
    fmt[bdt_CS.levels[0]] = r'$1.96\sigma$ $(BDT)$'
    fmt[bdt_CS.levels[1]] = r'$5\sigma$ $(BDT)$'
    manual_locations = [(1100,400),(1300,1000)]
    plt.clabel(bdt_CS, inline=1, fontsize=11, fmt=fmt,manual=manual_locations)
    X, Y, Z = get_XYZ_grid(cc_df,res)
    cc_CS = plt.contour(X,Y,Z,levels = [1.96,5], linestyles = 'solid', colors = colors)
    fmt[cc_CS.levels[0]] = '$1.96\sigma$'
    fmt[cc_CS.levels[1]] = '$5\sigma$'
    manual_locations = [(1300,800),(900,400)]
    plt.clabel(cc_CS, inline=1, fontsize=11, fmt=fmt,manual=manual_locations)

    make_line()
    set_axis_labels()
    plt.locator_params(axis='x',nbins=6)
    plt.locator_params(axis='y',nbins=6)
    # plt.text(600, 1200, r"${}\sigma$".format(levels[0]), fontsize = 30)

    plt.tight_layout()
    filename = 'combined'
    plt.savefig('images/{}.pdf'.format(filename),dpi = 300)


if __name__ == '__main__':
    if sys.argv[1] == '--collect':
        collect_max_bdt_sigs()
    elif sys.argv[1] == '--exclusion':
        make_contour_plot([1.96], 'exclusion',50,'DarkBlue')
    elif sys.argv[1] == '--discovery':
        make_contour_plot([5], 'discovery', 19,'Maroon')
    elif sys.argv[1] == '--combined':
        make_combined_contour_plot()
