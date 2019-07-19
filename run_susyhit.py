import sys
sys.path.insert(0,'/rsgrps/shufang/clusterpheno')
from clusterpheno.helpers import modify_file, cd
import subprocess as sp
import shutil as sh
from myProcesses import signals
from tqdm import tqdm
import os

susyhit_path = '/extra/adarsh/Tools/susyhit'
dm_dir = os.getcwd()
def set_params(mu,M1):
    def linemodfn(line):
        if 'M_1' in line:
            return '   1   {} # M_1\n'.format(M1)
        if '# mu(EWSB)' in line:
            return '   23\t{} # mu(EWSB)\n'.format(mu)
        else: return line
    modify_file('suspect2_lha.in', linemodfn)

def run_susyhit(signal):
    with cd(susyhit_path):
        set_params(signal.mH,signal.mB)
        sp.call('./run', 
                stdout = open(os.devnull,'w')
                )
        sp.call(['cp','susyhit_slha.out',
                 '/'.join([dm_dir,'Cards/param_cards/',
                           signal.index+'_param_card.dat'])])


if __name__ == "__main__":
    # map(run_susyhit,tqdm(signals, desc = 'running SUSY-HIT'))
    with cd(susyhit_path):
        set_params(1000, 25)
        sp.call('./run')
        sp.call(['cp','susyhit_slha.out',
                 '/'.join([dm_dir,'Cards/param_cards/',
                           signal.index+'_param_card.dat'])])

