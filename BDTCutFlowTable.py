from __future__ import division
from CutFlowTable import CutFlowTable
from helper_classes import Counter
from helper_functions import get_SAF_objects
import pandas as pd

class BDTCutFlowTable(CutFlowTable):

    def __init__(self, signal, Classifier, bdt_cut):
        self.signal = signal
        self.classifier = Classifier
        self.features = Classifier.features
        self.bdt_cut = bdt_cut

    def simulated_events_table(self):
        df = pd.DataFrame(index = ['After preselection','After BDT cut'])
        for proc in [self.classifier.signal]+self.classifier.backgrounds:
            df[proc.name] = [len(proc.test_set),
                             len(filter(lambda x: x > self.bdt_cut, 
                             self.classifier.clf.decision_function(proc.test_set)))]
        return df

    def original_xsection_for_xsection_table(self, proc):
        filename = '/'.join(['Make_ML_Arrays', 'Output', proc.name, 
                             'ML_Arrays', 'Cutflows', 'Signal'])
        n_orig = Counter((get_SAF_objects(filename)).InitialCounter).nevents
        return (len(proc.feature_array(self.features))/n_orig)*proc.xsection
