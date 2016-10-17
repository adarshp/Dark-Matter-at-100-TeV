from __future__ import division
import os
import contextlib
import subprocess as sp
import numpy as np

def change_directory(destination_directory):
    """ Temporarily changes the working directory. This is used with the 
    context manager, `cd`, given below:

    Example
    --------
    Here is an example of how one might use the function:

        with cd('relative/path/to/directory'):
            print(os.getcwd()) # Prints the working directory
            subprocess.call('./run_external_program') # Runs some non-python program

    Parameters
    ----------
    destination_directory : string
        The directory to temporarily change the working directory to. 

    """
    cwd = os.getcwd()
    os.chdir(destination_directory)
    try: yield
    except: pass
    finally: os.chdir(cwd)

cd = contextlib.contextmanager(change_directory)


class SignificanceCalculator:
    """ Class to calculate significance for a simple counting experiment.

    Example
    -------
    If, after cuts, we have the following events left over (for a given 
    luminosity) :

    Signal : 10 events
    Background 1 : 20 events ; tau_1 = 0.5
    Background 2 : 13 events ; tau_2 = 1.5
    Background 3 : 15 events ; tau_3 = 8

    Associated with each background is a factor 'tau', which parameterizes the
    uncertainty from the number of Monte Carlo events generated. For example,
    if we have the following:

    :math:`n_{M}C` = Number of Monte Carlo events generated for a background.
    :math:`\sigma_b = Cross-section for the background (output by the generator).
    :math:`\mathcal{L} = Luminosity for which we would like to calculate the significance.

    the factor tau for this background would be:

    ..math:
    \tau = n_mC/(sigma_b * L)

    Basically, the more Monte Carlo events you generate, that is, the greater
    the tau factor is, the more confident you can be that the number of 
    background events that you get after cuts will match what is seen at a detector.

    Here is a minimal working program that implements the above.

    
        from SignificanceCalculator import SignificanceCalculator

        s = 10
        b_tau_tuples = [(20, 0.5), (13, 1.5), (15, 8)]
        calc = SignificanceCalculator(s, b_tau_tuples)
        calc.print_report()
    
    This should return the following:
     
        $ The expected discovery significance is 0.612969
        $ The expected exclusion limit is 1.08637
        $ S/sqrt(B) = 1.56

    """

    def __init__(self, s, b_tau_tuples):
        """
        Parameters
        ----------
        s : int
            Number of expected signal events after cuts.
        b_tau_tuples : `list` of `tuple`
            List of tuples of the form (b_i, tau_i), where b_i is the number of
            events expected after cuts for background i. tau_i is a factor that 
            parameterizes the uncertainty in the number of background events.
        """
        self.s = s
        self.b_tau_tuples = b_tau_tuples
        self.b = sum([b_tau_tuple[0] for b_tau_tuple in self.b_tau_tuples])

    def write_SigCalc_inputFile(self, n_obs):
        """ Write an input file for SigCalc to process.

        Args:
            n_obs (int) : Number of events observed in the signal region.
        """
        with open('Tools/SigCalc/inputFile.txt', 'w') as f:
            f.write("# File for significance calculation with SigCalc\n")
            f.write("# n = observed number of events\n")
            f.write(str(n_obs)+"\n")
            f.write("# s = exp. # of events for the nominal signal model\n")
            f.write(str(self.s)+"\n")
            f.write("# m_i      tau_i\n")

            for b_tau_tuple in self.b_tau_tuples:
                f.write(str(b_tau_tuple[0])+"\t"+str(b_tau_tuple[1])+"\n")

    def run_SigCalc(self):
        """ Run SigCalc with the inputFile """ 
        with cd('Tools/SigCalc'):
            proc = sp.Popen(['./runSigCalc', 'inputFile.txt'],
                    stdout = sp.PIPE)
            return proc.stdout.readlines()

    def calculate_discovery_significance(self):
        """ Calculates the expected discovery significance. """
        self.write_SigCalc_inputFile(str(self.s + self.b))
        lines = filter(lambda line: line.startswith('Discovery'), self.run_SigCalc())
        return lines[0].split()[-1]

    def calculate_exclusion_limit(self):
        """ Calculates the expected exclusion limit """
        self.write_SigCalc_inputFile(str(self.b))
        return (self.run_SigCalc())[-2].split()[-1]

    def print_report(self):
        """ Prints a report with the expected discovery significance and 
        exclusion limit. 
        """
        disc_sig = self.calculate_discovery_significance()
        excl_lim = self.calculate_exclusion_limit()
        print("The expected discovery significance is {}".format(disc_sig))
        print("The expected exclusion limit is {}".format(excl_lim))
        print("S/sqrt(B) = ".format(str(self.s/np.sqrt(self.b))))

