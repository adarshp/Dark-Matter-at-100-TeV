#!/usr/bin/env python

from __future__ import division
import os
import sys
sys.path.insert(0, '/extra/adarsh/clusterpheno')
from clusterpheno.helpers import *
from myProcesses import signals
import matplotlib
# matplotlib.use('Agg')
matplotlib.use('pgf')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# For JHEP
# figwidth = 6.12
# plt.rcParams['figure.figsize'] = (figwidth,figwidth*3/4)

# For dissertation
pgf_with_rc_fonts = {
    "font.family": "serif",
    # "font.serif": ,
}

matplotlib.rcParams.update(pgf_with_rc_fonts)
def figsize(scale):
    fig_width_pt = 281.0
    inches_per_pt = 1.0/72.27
    golden_mean = (np.sqrt(5.0)-1.0)/2.0
    fig_width = fig_width_pt*inches_per_pt*scale
    fig_height = fig_width*golden_mean
    fig_size = [fig_width, fig_width]
    return fig_size

plt.style.use('ggplot')
plt.figure(figsize=figsize(1.0))
plt.rc('font',size=10)
plt.rc('xtick',labelsize=10)
plt.rc('ytick',labelsize=10)
plt.rc('axes',labelsize=10)

def get_max_bdt_significance(signal):
    with cd('MakeFeatureArrays/Output/'+signal.index+'/'):
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
    plt.plot(x,x,color = 'gray', linestyle = 'dashed', linewidth=1.0)

def set_axis_labels():
    plt.xlim(525,2000)
    plt.ylim(0,1500)
    plt.text(610, 1400, r"$\mathcal{L}=$ 3000 fb$^{-1}$", fontsize = 12)
    plt.text(700, 1050, r"$M_1 = |\mu|$", fontsize=10,rotation = 45)
    plt.ylabel(r'$M_1$ $\mathrm{(GeV)}$',fontsize=10)
    plt.xlabel(r'$|\mu|$ $\mathrm{(GeV)}$',fontsize=10)
    axes = plt.axes()
    # axes.xaxis.set_label_coords(0.1, -0.1)
    # axes.yaxis.set_label_coords(-0.08, 0.1)
    plt.tight_layout()

def make_contour_plot(levels, filename, res, colors):
    bdt_df = pd.read_csv('intermediate_results/bdt_sigs.txt')
    cc_df = pd.read_csv('intermediate_results/cc_max_sigs.txt')

    plt.style.use('ggplot')

    fmt = {}
    X, Y, Z = get_XYZ_grid(bdt_df,res)
    bdt_CS = plt.contour(X,Y,Z,levels = levels, linestyles = 'dashed', colors = colors)
    fmt[bdt_CS.levels[0]] = '$\mathrm{BDT}$'
    plt.clabel(bdt_CS, inline=1, fmt=fmt)
    X, Y, Z = get_XYZ_grid(cc_df,res)
    cc_CS = plt.contour(X,Y,Z,levels = levels, linestyles = 'solid', colors = colors)
    fmt[cc_CS.levels[0]] = '$\mathrm{CC}$'
    plt.clabel(cc_CS, inline=1, fmt=fmt)

    make_line()
    set_axis_labels()
    plt.text(600, 1200, r"${}\sigma$".format(levels[0]), fontsize = 14)

    plt.tight_layout()
    plt.savefig('images/{}.pdf'.format(filename))

def make_combined_contour_plot():
    bdt_df = pd.read_csv('intermediate_results/bdt_sigs.txt')
    cc_df = pd.read_csv('intermediate_results/cc_max_sigs.txt')

    res = 15
    fmt = {}
    X, Y, Z = get_XYZ_grid(bdt_df,res)
    colors = ['DarkBlue','Maroon']
    bdt_CS = plt.contour(X,Y,Z,levels = [1.96,5], linestyles = 'dashed', linewidths=1.0,colors = colors)

    # BDT contour labels
    fmt[bdt_CS.levels[0]] = r'1.96$\sigma$ (BDT)'
    fmt[bdt_CS.levels[1]] = r'5$\sigma$ (BDT)'
    manual_locations = [(1200,800),(1550,1200)]
    plt.clabel(bdt_CS, inline=1, fontsize=11, fmt=fmt,manual=manual_locations)

    X, Y, Z = get_XYZ_grid(cc_df,res)
    cc_CS = plt.contour(X,Y,Z,levels = [1.96,5],linewidths=1.0, linestyles = 'solid', colors = colors)
    fmt[cc_CS.levels[0]] = '1.96$\sigma$'
    fmt[cc_CS.levels[1]] = '5$\sigma$'
    manual_locations = [(1000,800),(850,400)]
    plt.clabel(cc_CS, inline=1, fontsize=11, fmt=fmt,manual=manual_locations)

    make_line()
    set_axis_labels()
    # plt.locator_params(axis='x', tick_values)
    # plt.locator_params(axis='y', )
    # plt.text(600, 1200, r"${}\sigma$".format(levels[0]), fontsize = 30)

    plt.tight_layout()
    filename = 'combined'
    plt.savefig('images/{}.pdf'.format(filename),dpi = 300)
    plt.savefig('images/{}.pgf'.format(filename))

if __name__ == '__main__':
    if sys.argv[1] == '--collect':
        collect_max_bdt_sigs()
    elif sys.argv[1] == '--exclusion':
        make_contour_plot([1.96], 'exclusion',50,'DarkBlue')
    elif sys.argv[1] == '--discovery':
        make_contour_plot([5], 'discovery', 19,'Maroon')
    elif sys.argv[1] == '--combined':
        make_combined_contour_plot()
