#!/usr/bin/env python

from __future__ import division
import numpy as np
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
matplotlib.rc('text', usetex = True)
matplotlib.rc('xtick', labelsize = 20)
matplotlib.rc('ytick', labelsize = 20)
matplotlib.rc('font', size = 20)

def s_sqrt_b(s,b):
    return s/np.sqrt(b)

def AMS2(s, b, br):
    return np.sqrt(2*((s+b+br)*np.log(1+(s/(b+br)))-s))

def make_contour_plot():
    x = np.arange(1, 50, 1)
    y = np.arange(1, 50, 1)
    plt.style.use('ggplot')
    X,Y = np.meshgrid(x,y)
    z1 = s_sqrt_b(X,Y)
    z2 = AMS2(X,Y, 3)
    CS1 = plt.contour(X, Y, z1, levels = [1.96, 5], colors = 'k')
    CS2 = plt.contour(X, Y, z2, levels = [1.96, 5])
    plt.clabel(CS1, inline = 1)
    plt.clabel(CS2, inline = 1)
    plt.xlabel('s')
    plt.ylabel('b')
    plt.savefig('ams.pdf')

if __name__ == '__main__':
    b = np.arange(1,100,0.1)
    plt.style.use('ggplot')
    s = 20
    plt.plot(b, AMS2(s, b, 0), label = r'$AMS_{2}(b_r = 0)$')
    plt.plot(b, AMS2(s, b, 3), label = r'$AMS_{2}(b_r = 3)$')
    plt.plot(b, s_sqrt_b(s, b), label = r'$S/\sqrt{B}$')
    plt.legend()
    plt.xscale('log')
    plt.xlabel(r'$b$')
    plt.ylabel(r'$\mathit{Significance}$')
    plt.savefig('ams.pdf')

