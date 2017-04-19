from tqdm import tqdm
from myProcesses import signals
import matplotlib
matplotlib.use('pgf')
matplotlib.rc('font', size = 10)
import numpy as np
import matplotlib.pyplot as plt
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
    fig_width = fig_width_pt*inches_per_pt
    fig_height = fig_width*golden_mean
    fig_size = [fig_width, fig_width]
    # fig_size = [1.9,1.9]
    return fig_size

plt.style.use('ggplot')
plt.figure(figsize=figsize(1.0))

signals = [signal for signal in signals if signal.mB == 25.0]
x = [signal.mH for signal in tqdm(signals)]
y = [1000.*signal.get_pair_prod_xsection() for signal in tqdm(signals)]
plt.style.use('ggplot')
plt.ylabel(r'$\sigma(pp\rightarrow\widetilde{\chi_2^0}\widetilde{\chi_3^0})$ $\mathrm{(fb)}$',fontsize = 8)
plt.xlabel(r'$\mu$ $\mathrm{(GeV)}$',fontsize = 8)
plt.xlim(500,2500)
plt.ylim(0.1,1000)
plt.semilogy(x,y)
plt.tight_layout()
plt.savefig('images/xsection_plot.pgf')
plt.savefig('images/xsection_plot.pdf')
# z = [signal.get_pair_prod_xsection() for signal in signals[0:10]]

