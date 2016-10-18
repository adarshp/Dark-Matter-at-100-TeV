#!/usr/bin/env python

import sys
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from tqdm import tqdm

def make_plot():
    # Generate data:
    df = pd.read_csv(sys.argv[1])

    x = df['Higgsino mass'] 
    y = df['Bino mass'] 
    z_disc = df['Discovery Significance']
    z_excl = df['Exclusion Limit']

    def grid(x, y, z, resX=100, resY=100):
        # Convert 3 column data to matplotlib grid
        xi = np.linspace(525, 4000, resX)
        yi = np.linspace(25, 2500, resY)
        X, Y = np.meshgrid(xi, yi)
        Z = matplotlib.mlab.griddata(x, y, z, xi, yi, interp='linear')
        return X, Y, Z

    X_disc, Y_disc, Z_disc = grid(x, y, z_disc)
    X_excl, Y_excl, Z_excl = grid(x, y, z_excl)

    # Plot dashed line
    x1 = np.arange(525, 2525, 100)
    y1 = x1
    plt.style.use('ggplot')
    plt.plot(x1, y1, c = 'grey', linestyle = 'dashed')

    CS_disc = plt.contour(X_disc, Y_disc, Z_disc, levels = [5])
    CS_excl = plt.contour(X_excl, Y_excl, Z_excl, levels = [1.96])
    plt.text(700, 2200, r'$\mathcal{L} = 3000 \mathrm{ab}^{-1}$', fontsize=20)
    plt.clabel(CS_disc, inline=1, fontsize=10, fmt='%1.0f')
    plt.clabel(CS_excl, inline=1, fontsize=10, fmt='%1.0f')
    plt.xlabel(r'$m_{NLSP}$ (GeV)')
    plt.ylabel(r'$m_{LSP}$ (GeV)')

    plt.savefig('contours.png')

def main():
    make_plot()
    
if __name__ == '__main__':
    main()
