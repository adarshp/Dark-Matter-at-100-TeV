from Process import Process
from SignalProcess import SignalProcess
import numpy as np
from tqdm import tqdm
import itertools as it
from glob import glob

MassCombination = namedtuple('MassCombination', 'mH mB')

def mass_combinations(min_higgsino_mass, max_higgsino_mass,
                               higgsino_mass_step_size,min_bino_mass,
                               max_bino_mass,bino_mass_step_size):

    """ Generate mass combinations of higgsino and bino masses. """
    higgsino_masses = np.arange(min_higgsino_mass, max_higgsino_mass,
                                higgsino_mass_step_size)

    bino_masses = np.arange(min_bino_mass, max_bino_mass, 
                            bino_mass_step_size)

    tuples = list(it.product(higgsino_masses, bino_masses))
    namedtuples = [MassCombination(*_tuple) for _tuple in tuples] 
    return filter(lambda x.mH > x.mB, namedtuples)

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
