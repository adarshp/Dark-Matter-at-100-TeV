import sys
sys.path.insert(0, '../clusterpheno')
from clusterpheno.Process import Process
from clusterpheno.helpers import cd, modify_file
import numpy as np
from tqdm import tqdm
import itertools as it
from glob import glob
import shutil as sh
from collections import namedtuple

MassCombination = namedtuple('MassCombination', 'mH mB')

def mass_combinations(mH_min, mH_max, mH_step_size, mB_min, mB_max, mB_step_size):

    """ Generate mass combinations of higgsino and bino masses. """

    higgsino_masses = np.arange(mH_min, mH_max, mH_step_size)
    bino_masses = np.arange(mB_min, mB_max, mB_step_size)

    tuples = list(it.product(higgsino_masses, bino_masses))
    namedtuples = [MassCombination(*_tuple) for _tuple in tuples] 
    return filter(lambda x: x.mH > x.mB, namedtuples)

class SignalProcess(Process):
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
        self.index = '_'.join(["mH", str(int(self.mH)), "mB", str(int(self.mB))])
        Process.__init__(self, 
            'H1H2', 'mssm-full', 'bbll_MET', 
        """import model mssm-full
        generate p p > n2 n3, (n2 > n1 z, z > l+ l-), (n3 > n1 h1, h1 > b b~)
        add process p p > n2 n3, (n3 > n1 z, z > l+ l-), (n2 > n1 h1, h1 > b b~)
        """, 100, self.index) 

    def get_xsection(self):
        with open('prospino_output/'+self.name+'_xsection.dat', 'r') as f:
            xs = float(f.readlines()[0].split()[-1:][0])

        xs = xs*1000.0 # Convert from attobarns to fb
        xs = xs*0.58 # Apply h->bb branching ratio
        xs = xs*0.067 # Apply Z->ll branching ratio
        xs = xs*0.5 # Apply Goldstone equivalence theorem

        return xs

    def run_susyhit(self, susyhit_path = 'Tools/susyhit'):
        with cd(susyhit_path):
            with open('suspect2_lha.in', 'w') as f:
                f.write(suspect_input_template.format(mH=str(self.mH),
                        mB=str(self.mB), mW="3000.",tb="10.0"))
            sp.call('./run', stdout = open(os.devnull, 'w'))
            sh.copy('slhaspectrum.in', 
                '../../Cards/prospino_input/'+self.index+'_slhaspectrum.in')
            sh.copy('susyhit_slha.out', '../../Cards/param_cards/'+self.index+'_param_card.dat')

    
    def copy_param_card(self):
        name = 'mH_{}_mB_{}'.format(str(int(self.mH)), str(int(self.mB)))
        sh.copy('Cards/param_cards/{}_param_card.dat'.format(name),
                self.directory+'/Cards/param_card.dat')

    def copy_bdt_analysis(self):
        sh.rmtree(self.directory+'/MakeFeatureArray')
        sh.copytree('MakeFeatureArray', self.directory+'/MakeFeatureArray')


signals = [SignalProcess(bp) for bp in mass_combinations(500.0, 4000.0, 100.0,
                                                         25.0, 2500.0, 100.0)]

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
