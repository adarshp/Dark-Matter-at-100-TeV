from Process import Process

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
        Process.__init__(self, 
            'Signal', 'mssm-full', 'bbll_MET', 
        """import model mssm-full
        generate p p > n2 n3, (n2 > n1 z, z > l+ l-), (n3 > n1 h1, h1 > b b~)
        add process p p > n2 n3, (n3 > n1 z, z > l+ l-), (n2 > n1 h1, h1 > b b~)
        """, 100, self.index()) 

    def index(self):
        return '_'.join(["mH", str(int(self.mH)), "mB", str(int(self.mB))])

    def get_xsection(self):
        with open('prospino_output/'+self.name+'_xsection.dat', 'r') as f:
            xs = float(f.readlines()[0].split()[-1:][0])

        xs = xs*1000.0 # Convert from attobarns to fb
        xs = xs*0.58 # Apply h->bb branching ratio
        xs = xs*0.067 # Apply Z->ll branching ratio
        xs = xs*0.5 # Apply Goldstone equivalence theorem

        return xs
    def run_susyhit(self):
        with cd('Tools/susyhit'):
            with open('suspect2_lha.in', 'w') as f:
                f.write(suspect_input_template.format(mH=str(self.mH),
                        mB=str(self.mB), mW=str(3000.),tb=str(10.0)))
            sp.call('./run', stdout = open(os.devnull, 'w'))
            sh.copy('slhaspectrum.in', '../../prospino_input/'+self.name+'_slhaspectrum.in')
            sh.copy('susyhit_slha.out', '../../Cards/param_cards/'+self.name+'_param_card.dat')

    def run_prospino(self, input_spectrum, prospino_directory,
                    output_directory):

        """ Runs Prospino to get the Higgsino pair production cross section. """

        sh.copy(input_spectrum, prospino_directory+'/prospino.in.les_houches')

        with cd(prospino_directory):
            subprocess.call(['make', 'clean'], stdout = devnull)
            subprocess.call('make', stdout = devnull)
            subprocess.call('./prospino_2.run', stdout = devnull)

        sh.copy(prospino_directory+'/prospino.dat', 
                output_directory+'/'+self.name+'_xsection.dat')
