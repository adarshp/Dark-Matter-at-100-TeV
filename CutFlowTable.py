from __future__ import division
from myProcesses import myProcesses
from helper_classes import OriginalEvents, SkimmedEvents
from SignificanceCalculator import SignificanceCalculator

class CutFlowTable:

    processes = myProcesses()
    backgrounds = processes.backgrounds

    def __init__(self, signal, razor_vars):
        self.razor_vars = razor_vars
        self.signal = signal 

    def simulated_events_table(self):
        def replace_rows(process, razor_vars):
            df1 = OriginalEvents(process).events
            df2 = SkimmedEvents(process, razor_vars).events
            df1[process.name]['m_R'] = df2[process.name+'_skimmed']['m_R']
            df1[process.name]['m_T_R'] = df2[process.name+'_skimmed']['m_T_R']
            return df1 
        signal_events = replace_rows(self.signal, self.razor_vars)
        bg_events = [replace_rows(bg, self.razor_vars) for bg in self.backgrounds]
        return signal_events.join(bg_events)

    def original_xsection_for_xsection_table(self, process):
        return process.xsection

    def xsection_table(self):
        df = self.simulated_events_table()
        for process in [self.signal]+self.backgrounds:
            xsection = self.original_xsection_for_xsection_table(process)
            df[process.name] = xsection*df[process.name]/(df[process.name][0])
        # df['Total BG xsection'] = sum([df[bg.name] for bg in self.backgrounds])
        # df['S/B'] = df[self.signal.name]/df['Total BG xsection']
        return df

    def events_table(self):
        """ luminosity in attobarns """
        df = self.xsection_table()
        luminosity = 3000.
        for process in [self.signal]+self.backgrounds:
            df[process.name] = (df[process.name]*luminosity).astype(int)
        df['n_S'] = df[self.signal.name]
        df['n_B']= sum([df[bg.name] for bg in self.backgrounds])
        df['S/B'] = df['n_S']/df['n_B']
        return df

    def tau(self, bg):
        xs = self.original_xsection_for_xsection_table(bg)
        return (self.simulated_events_table()[bg.name][0]/(xs*3000.))

    def initialize_significance_calculator(self):
        df = self.events_table()
        bg_tau_tuples = [(df[bg.name][-1], self.tau(bg)) for bg in self.backgrounds]
        return SignificanceCalculator(df['n_S'][-1], bg_tau_tuples, self.signal)
