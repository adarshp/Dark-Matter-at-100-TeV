#!/usr/bin/env python
from tqdm import tqdm
from myProcesses import signals
import matplotlib
# matplotlib.use('pgf')
matplotlib.rc('font', size = 12)
matplotlib.rc('text', usetex=True)
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from math import atan2,degrees
import numpy as np

#Label line with line2D label data
def labelLine(line,x,label=None,align=True,**kwargs):

    ax = line.axes
    xdata = line.get_xdata()
    ydata = line.get_ydata()

    if (x < xdata[0]) or (x > xdata[-1]):
        print('x label location is outside data range!')
        return

    #Find corresponding y co-ordinate and angle of the
    ip = 1
    for i in range(len(xdata)):
        if x < xdata[i]:
            ip = i
            break

    y = ydata[ip-1] + (ydata[ip]-ydata[ip-1])*(x-xdata[ip-1])/(xdata[ip]-xdata[ip-1])

    if not label:
        label = line.get_label()

    if align:
        #Compute the slope
        dx = xdata[ip] - xdata[ip-1]
        dy = ydata[ip] - ydata[ip-1]
        ang = degrees(atan2(dy,dx))

        #Transform to screen co-ordinates
        pt = np.array([x,y]).reshape((1,2))
        trans_angle = ax.transData.transform_angles(np.array((ang,)),pt)[0]

    else:
        trans_angle = 0

    #Set a bunch of keyword arguments
    if 'color' not in kwargs:
        kwargs['color'] = line.get_color()

    if ('horizontalalignment' not in kwargs) and ('ha' not in kwargs):
        kwargs['ha'] = 'center'

    if ('verticalalignment' not in kwargs) and ('va' not in kwargs):
        kwargs['va'] = 'center'

    if 'backgroundcolor' not in kwargs:
        kwargs['backgroundcolor'] = ax.get_facecolor()

    if 'clip_on' not in kwargs:
        kwargs['clip_on'] = True

    if 'zorder' not in kwargs:
        kwargs['zorder'] = 2.5

    ax.text(x,y,label,rotation=trans_angle,fontsize=8,**kwargs)

def labelLines(lines,align=True,xvals=None,**kwargs):

    ax = lines[0].axes
    labLines = []
    labels = []

    #Take only the lines which have labels other than the default ones
    for line in lines:
        label = line.get_label()
        if "_line" not in label:
            labLines.append(line)
            labels.append(label)

    if xvals is None:
        xmin,xmax = ax.get_xlim()
        xvals = np.linspace(xmin,xmax,len(labLines)+2)[1:-1]

    for line,x,label in zip(labLines,xvals,labels):
        labelLine(line,x,label,align,**kwargs)

filename = 'branching_ratios.dat'
pgf_with_rc_fonts = {
    "font.family": "serif",
    "font.sans-serif":"Helvetica"
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

plt.figure(figsize=figsize(1.0))
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

def make_contour_plot():
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

    fmt = {}

    xline = np.arange(525,2500, 0.1) 
    fig1 = plt.figure()
    cs1 = plt.contour(X,Y,Z1)
    plt.title('hh')
    plt.clabel(cs1,inline=1)
    plt.savefig('images/hh.pdf')
    plt.cla()

    cs2 = plt.contour(X,Y,Z2)
    plt.clabel(cs2,inline=1)
    plt.title(r'BR$(\widetilde{\chi}_{2}^0\widetilde{\chi}_3^0\rightarrow \widetilde{\chi}_1^0\widetilde{\chi}_1^0+hZ)$')
    plt.ylabel('M$_1$')
    plt.xlabel('$\mu$')
    plt.savefig('images/hZ.pdf')
    plt.cla()

    plt.plot(xline,xline,color = 'gray', linestyle = 'dashed', linewidth=1.0)
    cs3 = plt.contour(X,Y,Z3)
    plt.title('ZZ')
    plt.clabel(cs3,inline=1)
    plt.savefig('images/ZZ.pdf')

    plt.savefig('images/br_contours.pdf')

def make_plot():
    """ Plot branching ratio of a individual neutralinos"""
    df = pd.read_csv(filename)
    df = df[df['M1'] == 25]
    x = df['mu']
    y1 = df['br_chi2_Zchi1']
    y2 = df['br_chi2_hchi1']
    y3 = df['br_chi3_Zchi1']
    y4 = df['br_chi3_hchi1']
    y5 = y1*y4 + y2*y3
    plt.xlabel(r'$\mu$ (GeV)',fontsize=12)
    plt.ylabel('Branching fraction',fontsize=12)
    plt.plot(x,y1, label = '$\widetilde{\chi}_2^0\\rightarrow \widetilde{\chi}_1^0 Z$')
    plt.plot(x,y2, label = '$\widetilde{\chi}_2^0\\rightarrow \widetilde{\chi}_1^0 h$')
    plt.plot(x,y3, label = '$\widetilde{\chi}_3^0\\rightarrow \widetilde{\chi}_1^0 Z$')
    plt.plot(x,y4, label = '$\widetilde{\chi}_3^0\\rightarrow \widetilde{\chi}_1^0 h$')
    plt.xlim(500, 4000)
    plt.ylim(0.3, 0.7)
    lines = plt.gca().get_lines()
    labelLines(lines, align = True, xvals = [2500, 2500, 3500, 3500])
    plt.tight_layout()
    plt.savefig('images/br_plot.pdf')
    # plt.savefig('images/br_plot.pgf')

if __name__ == '__main__':
    make_plot()
