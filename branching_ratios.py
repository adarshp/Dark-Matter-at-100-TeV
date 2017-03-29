#!/usr/bin/env python
from tqdm import tqdm
from myProcesses import signals
import matplotlib
matplotlib.use('Agg')
matplotlib.rc('text', usetex = True)
matplotlib.rc('xtick', labelsize = 11)
matplotlib.rc('ytick', labelsize = 11)
matplotlib.rc('font', size = 11)
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

filename = 'branching_ratios.dat'

def write_all_branching_ratios():
    with open(filename,'w') as f:
        f.write('mu,M1,br_chi2_Zchi1,br_chi2_hchi1,br_chi3_Zchi1,br_chi3_hchi1\n')
    for signal in tqdm(signals, desc='Writing branching ratios to file'):
        with open('Cards/param_cards/'+signal.index+'_param_card.dat','r') as f:
            for line in f.readlines():
                if 'BR(~chi_20 -> ~chi_10   Z )' in line:
                    br_chi2_Zchi1 = float(line.split()[0])
                if 'BR(~chi_20 -> ~chi_10   h )' in line:
                    br_chi2_hchi1 = float(line.split()[0])
                if 'BR(~chi_30 -> ~chi_10   Z )' in line:
                    br_chi3_Zchi1 = float(line.split()[0])
                if 'BR(~chi_30 -> ~chi_10   h )' in line:
                    br_chi3_hchi1 = float(line.split()[0])
        with open(filename, 'a') as f:
            f.write('{},{},{},{},{},{}\n'.format(signal.mH,
                                        signal.mB,
                                        br_chi2_Zchi1,
                                        br_chi2_hchi1,
                                        br_chi3_Zchi1,
                                        br_chi3_hchi1))

def make_plot():
    df = pd.read_csv(filename)
    res = 20
    resX = res; resY = res

    x = df['mu']
    y = df['M1']

    # hh
    z1 = df['br_chi3_hchi1']*df['br_chi2_hchi1']
    # hZ
    z2 = df['br_chi2_hchi1']*df['br_chi3_Zchi1']+df['br_chi3_hchi1']*df['br_chi2_Zchi1']
    # ZZ
    z3 = df['br_chi3_Zchi1']*df['br_chi2_Zchi1']

    xi = np.linspace(525, 4000, resX)
    yi = np.linspace(25, 1500, resY)
    X, Y = np.meshgrid(xi, yi)

    Z1 = matplotlib.mlab.griddata(x,y,z1,xi,yi,interp='nn')
    Z2 = matplotlib.mlab.griddata(x,y,z2,xi,yi,interp='nn')
    Z3 = matplotlib.mlab.griddata(x,y,z3,xi,yi,interp='nn')

    plt.style.use('ggplot')
    fmt = {}

    cs1 = plt.contour(X,Y,Z1, levels = [0.2])
    fmt[cs1.levels[0]] = 'hh, 0.2'
    plt.clabel(cs1,inline=1, fmt=fmt)

    cs2 = plt.contour(X,Y,Z2)
    # fmt[cs2.levels[0]] = 'hZ, 0.4'
    plt.clabel(cs2,inline=1)

    cs3 = plt.contour(X,Y,Z3, levels = [0.2])
    fmt[cs1.levels[0]] = 'ZZ, 0.2'
    plt.clabel(cs3,inline=1, fmt=fmt)

    plt.savefig('images/br_contours.pdf')

if __name__ == '__main__':
    make_plot()
