import os
import sys
import itertools as it
from ConfigParser import SafeConfigParser
import shutil as sh
from collections import namedtuple
import subprocess as sp
sys.path.insert(0, '../clusterpheno')
from clusterpheno.Process import Process
from clusterpheno.helpers import cd, modify_file, get_SAF_objects, Counter
import numpy as np
from tqdm import tqdm

DM_DIR="/home/u13/adarsh/Dark-Matter-at-100-TeV"
DM_CARDS_DIR="/home/u13/adarsh/Dark-Matter-at-100-TeV/Cards"
PROSPINO_DIR="/home/u13/adarsh/Prospino2/"

class Counter:
    def __init__(self, counter_object):
        cdata = counter_object.cdata.split('\n')
        self.name = cdata[1].split('\"')[1]
        self.nevents = int(cdata[2].split(' ')[0])

class Signal(Process):
    def __init__(self, benchmark_point):
        """
        Parameters
        ----------

        benchmark_point : namedtuple
            A named tuple containing the higgsino mass and bino mass.
        """
        self.bp = benchmark_point
        self.mH = self.bp.mH
        self.mB = self.bp.mB
        self.index = "_".join(["mH", str(int(self.mH)), "mB", str(int(self.mB))])
        Process.__init__(self,
            'H1H2', 'mssm-full', 'bbll_MET',
        """
        generate p p > n2 n3, (n2 > n1 z, z > l+ l-), (n3 > n1 h1, h1 > b b~)
        add process p p > n2 n3, (n3 > n1 z, z > l+ l-), (n2 > n1 h1, h1 > b b~)
        """, 100, self.index)

    def get_pair_prod_xsection(self):
        with open(DM_CARDS_DIR+'/prospino_output_xsections/'+self.index+'_xsection.dat', 'r') as f:
            xs = float(f.readlines()[0].split()[-1:][0])
        return xs

    def get_branching_ratios(self):
        with open(self.directory+'/Cards/param_card.dat','r') as f:
           for line in f.readlines():
                if 'BR(~chi_20 -> ~chi_10   Z )' in line:
                    self.br2_Z = float(line.split()[0])
                if 'BR(~chi_20 -> ~chi_10   h )' in line:
                    self.br2_h = float(line.split()[0])
                if 'BR(~chi_30 -> ~chi_10   Z )' in line:
                    self.br3_Z = float(line.split()[0])
                if 'BR(~chi_30 -> ~chi_10   h )' in line:
                    self.br3_h = float(line.split()[0])
                if 'BR(h -> b       bb     )' in line:
                    self.brh_bb = float(line.split()[0])
        
    def get_xsection(self):
        with open(DM_CARDS_DIR+'/prospino_output_xsections/'+self.index+'_xsection.dat', 'r') as f:
            xs = float(f.readlines()[0].split()[-1:][0])
        self.get_branching_ratios()
        xs = xs*1000.0 # Convert from attobarns to fb
        # Total branching fraction to Zh final state (from SUSY-HIT)
        xs = xs*(self.br2_Z*self.br3_h + self.br3_Z*self.br2_h) 
        xs = xs*self.brh_bb # Apply h->bb branching ratio
        xs = xs*0.067 # Apply Z->ll branching ratio
        # xs = xs*0.5 # Apply Goldstone equivalence theorem
        return xs

    def run_susyhit(self, susyhit_path = '/extra/adarsh/Tools/susyhit'):
        with cd(susyhit_path):
            with open('suspect2_lha.in', 'w') as f:
                f.write(suspect_input_template.format(mH=str(self.mH),
                        mB=str(self.mB), mW="3000.",tb="10.0"))
            sp.call('./run', stdout = open(os.devnull, 'w'))
            sh.copy('slhaspectrum.in',
                DM_CARDS_DIR+'/prospino_input/'+self.index+'_slhaspectrum.in')
            sh.copy('susyhit_slha.out', DM_CARDS_DIR+'/param_cards/'+self.index+'_param_card.dat')


    def copy_param_card(self):
        name = 'mH_{}_mB_{}'.format(str(int(self.mH)), str(int(self.mB)))
        sh.copy(DM_CARDS_DIR+'/param_cards/{}_param_card.dat'.format(name),
                self.directory+'/Cards/param_card.dat')

    def copy_bdt_analysis(self):
        sh.rmtree(self.directory+'/MakeFeatureArray')
        sh.copytree('MakeFeatureArray', self.directory+'/MakeFeatureArray')

    def write_pbs_script(self, parser, nruns):
        with open(parser.get('PBS Templates', 'generate_script'), 'r') as f:
            string = f.read()
        with open(self.directory+'/generate_events.pbs', 'w') as f:
            f.write(string.format(jobname = str(int(self.mH))+'_'+str(int(self.mB)),
                                  username = parser.get('Cluster', 'username'),
                                  email = parser.get('Cluster', 'email'),
                                  group_list = parser.get('Cluster', 'group_list'),
                                  nruns = str(nruns),
                                  cput = str(7*nruns),
                                  walltime = str(7*nruns),
                                  cwd = os.getcwd(),
                                  mg5_process_dir = self.directory))

    def run_prospino(self):
        """ Runs Prospino to get the Higgsino pair production cross section. """

        input_spectrum = DM_CARDS_DIR+'/prospino_input/'+self.index+'_slhaspectrum.in'
        sh.copy(input_spectrum, PROSPINO_DIR+'/prospino.in.les_houches')

        with cd(PROSPINO_DIR):
            devnull = open(os.devnull, 'w')
            sp.call(['make', 'clean'])
            sp.call('make')
            sp.call('./prospino_2.run')
            sh.copy('prospino.dat',
                DM_CARDS_DIR+'/prospino_output_xsections/'+self.index+'_xsection.dat')

    def make_feature_array(self):
        with cd(self.directory+'/MakeFeatureArray/Build'):
            devnull = open(os.devnull, 'w')
            sp.call('./analyze.sh', shell = True,
                    stderr = devnull,
                    stdout = devnull)

    def get_original_nevents(self):
        filepath = self.directory+'/MakeFeatureArray/Output/Signal/Analysis/Cutflows/Signal'
        return Counter((get_SAF_objects(filepath)).InitialCounter).nevents

MassCombination = namedtuple('MassCombination', 'mH mB')

def mass_combinations(mH_min, mH_max, mH_step_size, mB_min, mB_max, mB_step_size):

    """ Generate mass combinations of higgsino and bino masses. """

    higgsino_masses = np.arange(mH_min, mH_max, mH_step_size)
    bino_masses = np.arange(mB_min, mB_max, mB_step_size)

    tuples = list(it.product(higgsino_masses, bino_masses))
    namedtuples = [MassCombination(*_tuple) for _tuple in tuples]
    return filter(lambda x: x.mH > x.mB + 126., namedtuples)

signals = [Signal(bp) for bp in mass_combinations(500.0, 2000.0, 100.0,
                                                  25.0, 1500.0, 100.0)]

tt_collection = [Process(
    'tt','sm','bbllvv',
    """generate p p > t t~, (t > w+ b, w+ > l+ vl), (t~ > w- b~, w- > l- vl~)""",
    100, i) for i in range(0, 30)]

tbW_collection = [Process(
    'tbW','sm','bbllvv',
    """generate p p > t w- b~ / t~, w- > l- vl~
    add process p p > t~ w+ b / t, w+ > l+ vl""",100, i) for i in range(0, 30)]

bbWW_collection = [Process(
    'bbWW','sm','bbllvv',"""\
    define vv = vl vl~
    define w = w+ w-
    define ll = l+ l-
    define tt = t t~
    define bb = b b~
    generate p p > bb bb w w / tt, ( w > ll vv, w > ll vv )""",
    100, i) for i in range(0, 30)]

backgrounds = tt_collection + tbW_collection + bbWW_collection

#tt.xsection = 17425.0
#tbW.xsection = 1488.0
#bbWW.xsection = 73.0
if __name__ == "__main__":
    for signal in tqdm(signals[0:1]):
        signal.run_susyhit()
        signal.run_prospino()
