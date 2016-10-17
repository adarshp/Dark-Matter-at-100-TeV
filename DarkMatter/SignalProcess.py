import os, glob
import subprocess as sp
from Process import Process
import shutil as sh
from helpers import cd, modify_file
from collections import namedtuple

class SignalProcess(Process):
    def __init__(self, benchmark_point):
        """
        Parameters
        ----------
        
        benchmark_point : namedtuple
            A named tuple containing the higgsino mass and bino mass.
        """
        self.bp = benchmark_point
        Process.__init__(self, 
            'Signal', 'mssm-full', 'bbll_MET', 
            mg5_generation_syntax = """\
              import model mssm-full
              generate p p > n2 n3, (n2 > n1 z, z > l+ l-), (n3 > n1 h1, h1 > b b~)
              add process p p > n2 n3, (n3 > n1 z, z > l+ l-), (n2 > n1 h1, h1 > b b~)""",
            index = self.index()) 

    def index(self):
        return '_'.join(["mH", self.bp.mH, "mB", self.bp.mB])

A_HZ_bbll_14_TeV_collection = [TwoHiggsDoubletModelProcess(
        name = 'A_HZ',
        decay_channel = 'bbll',
        mg5_generation_syntax = """\
        generate g g > h3 , ( h3 > h2 z , h2 > b b~ , z > l+ l- )""",
        energy = 14,
        benchmark_point = bp,
    ) for bp in BP_IA]

MassCombination = namedtuple('MassCombination', 'mH mB')

def generate_mass_combinations(min_higgsino_mass, max_higgsino_mass,
                               higgsino_mass_step_size,min_bino_mass,
                               max_bino_mass,bino_mass_step_size):

    """ Generate mass combinations of higgsino and bino masses. """
    higgsino_masses = np.arange(min_higgsino_mass, max_higgsino_mass,
                                higgsino_mass_step_size)

    bino_masses = np.arange(min_bino_mass, max_bino_mass, 
                            bino_mass_step_size)

    mass_combo_tuples = list(it.product(higgsino_masses, bino_masses))
    namedtuples = [MassCombination(*tuple) for tuple in mass_combo_tuples] 
    filteredtuples = filter(lambda x.mH > x.mB, namedtuples)

mass_combinations = generate_mass_combinations(500.0, 4000.0, 100.0,
                                                25.0, 2500.0, 100.0)
