import subprocess as sp
from helper_functions import cd

class SignificanceCalculator:

    def __init__(self, s, b_tau_tuples, signal):
        self.s = s
        self.b_tau_tuples = b_tau_tuples
        self.b = sum([b_tau_tuple[0] for b_tau_tuple in self.b_tau_tuples])
        self.signal = signal

    def write_SigCalc_inputFile(self, n_obs, filename):
        with open('Tools/SigCalc/{}'.format(filename), 'w') as f:
            f.write("# File for significance calculation with SigCalc\n")
            f.write("# n = observed number of events\n")
            f.write(str(n_obs)+"\n")
            f.write("# s = exp. # of events for the nominal signal model\n")
            f.write(str(self.s)+"\n")
            f.write("# m_i      tau_i\n")

            for b_tau_tuple in self.b_tau_tuples:
                f.write(str(b_tau_tuple[0])+"\t"+str(b_tau_tuple[1])+"\n")

    def run_SigCalc(self, filename):
        with cd('Tools/SigCalc'):
            proc = sp.Popen(['./runSigCalc', filename],
                    stdout = sp.PIPE)
            return proc.stdout.readlines()

    def calculate_discovery_significance(self, kind):
        """kind = cutandcount or bdt"""
        filename = self.signal.name+'_'+kind+'_discovery.txt'
        self.write_SigCalc_inputFile(str(self.s + self.b), filename)
        return (self.run_SigCalc(filename))[7].split()[-1]

    def calculate_exclusion_limit(self, kind):
        filename = self.signal.name+'_'+kind+'_exclusion.txt'
        self.write_SigCalc_inputFile(str(self.b), filename)
        return (self.run_SigCalc(filename))[-2].split()[-1]
