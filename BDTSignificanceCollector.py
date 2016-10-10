from SignificanceCollector import SignificanceCollector
from Classifier import Classifier
import numpy as np
from tqdm import tqdm
from BDTCutFlowTable import BDTCutFlowTable
from pathos.multiprocessing import ProcessingPool as Pool

class BDTSignificanceCollector(SignificanceCollector):

    def collect_significances(self):
        with open(self.filename, 'w') as f:
            f.write("Higgsino mass,Bino mass,Discovery Significance,Exclusion Limit\n")
        
        def get_disc_sig(signal, classifier, bdt_cut):
            try:
                table = BDTCutFlowTable(signal, classifier, bdt_cut)
                calc = table.initialize_significance_calculator()
                sig = calc.calculate_discovery_significance('bdt')
                return sig
            except:
                pass

        def get_excl_lim(signal, classifier, bdt_cut):
            try:
                table = BDTCutFlowTable(signal, classifier, bdt_cut)
                calc = table.initialize_significance_calculator()
                lim = calc.calculate_exclusion_limit('bdt')
                return lim
            except:
                pass

        mySignals = self.signals

        pbar = tqdm(total = len(mySignals)/8)

        def write_sigs(signal):
            try:
                classifier = Classifier(signal.mass_combination_tuple) 
                discs = map(lambda x: get_disc_sig(signal, classifier, x),
                        np.arange(-10, 10, 0.1))
                excls = map(lambda x: get_excl_lim(signal, classifier, x), 
                        np.arange(-10, 10, 0.1))

                with open(self.filename, 'a') as f:
                    f.write("{},{},{},{}\n".format(signal.higgsino_mass, 
                                                signal.bino_mass,
                                                max(discs),
                                                max(excls)))
                pbar.update(1)
            except:
                pass

        p = Pool(8)
        p.map(write_sigs, mySignals)
        
