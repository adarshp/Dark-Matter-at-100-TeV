from tqdm import tqdm
from myProcesses import signals
import matplotlib
matplotlib.use('Agg')
matplotlib.rc('text', usetex = True)
matplotlib.rc('xtick', labelsize = 11)
matplotlib.rc('ytick', labelsize = 11)
matplotlib.rc('font', size = 11)
import numpy as np
import matplotlib.pyplot as plt
figwidth = 4
plt.rcParams['figure.figsize'] = (figwidth,figwidth*3/4)

signals = [signal for signal in signals if signal.mB == 25.0]
x = [signal.mH for signal in tqdm(signals)]
y = [1000.*signal.get_pair_prod_xsection() for signal in tqdm(signals)]
plt.style.use('ggplot')
plt.ylabel(r'$\sigma(pp\rightarrow\widetilde{\chi_2^0}\widetilde{\chi_3^0})$ $\mathrm{(fb)}$',fontsize = 11)
plt.xlabel(r'$\mu$ $\mathrm{(GeV)}$',fontsize = 11)
plt.plot(x,y)
plt.tight_layout()
plt.savefig('xsection_plot.pdf')
# z = [signal.get_pair_prod_xsection() for signal in signals[0:10]]

