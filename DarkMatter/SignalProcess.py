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
