from myProcesses import myProcesses
import matplotlib
matplotlib.use('Agg')
import pylab
import numpy as np

processes = myProcesses()
x = [signal.higgsino_mass for signal in processes.signals]
y = [signal.bino_mass for signal in processes.signals]
z = [signal.xsection for signal in processes.signals]

def grid(x, y, z, resX=100, resY=100):
    # Convert 3 column data to matplotlib grid
    xi = np.linspace(min(x), max(x), resX)
    yi = np.linspace(min(y), max(y), resY)
    Z = matplotlib.mlab.griddata(x, y, z, xi, yi, interp='linear')
    X, Y = np.meshgrid(xi, yi)
    return X, Y, Z

X, Y, Z = grid(x, y, z)

pylab.contour(X, Y, Z, levels = [0.01, 0.1, 0.2])
pylab.xlim([0, 3000])
pylab.ylim([0, 1000])

# pylab.plot(x, y, 'bo')
pylab.savefig('xsectionplot.pdf')
