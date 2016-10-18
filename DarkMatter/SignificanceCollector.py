#!/usr/bin/env python

from myProcesses import myProcesses
from tqdm import tqdm
from helper_functions import razor_combinations
from CutFlowTable import CutFlowTable
from pathos.multiprocessing import ProcessingPool as Pool

class SignificanceCollector:

    processes = myProcesses()
    signals = processes.signals 
    razor_combos = razor_combinations()

    def __init__(self, filename):
        self.filename = filename
        
    def collect_significances(self):
        with open(self.filename, 'w') as f:
            f.write("Higgsino mass,Bino mass,Discovery Significance,Exclusion Limit\n")
        
        def get_disc_sig(signal, razor_combo):
            try:
                table = CutFlowTable(signal, razor_combo)
                calc = table.initialize_significance_calculator()
                return calc.calculate_discovery_significance('cutandcount')
            except:
                pass

        def get_excl_lim(signal, razor_combo):
            try:
                table = CutFlowTable(signal, razor_combo)
                calc = table.initialize_significance_calculator()
                return calc.calculate_exclusion_limit('cutandcount')
            except:
                pass

        for signal in tqdm(self.signals):

            try:
                p = Pool(8)
                myRazorCombos = self.razor_combos
                discs = p.map(lambda x: get_disc_sig(signal, x), myRazorCombos)
                excls = p.map(lambda x: get_excl_lim(signal, x), myRazorCombos)

                with open(self.filename, 'a') as f:
                    f.write("{},{},{},{}\n".format(signal.higgsino_mass, 
                                                   signal.bino_mass,
                                                   max(discs),
                                                   max(excls)))
            except KeyboardInterrupt:
                pass
