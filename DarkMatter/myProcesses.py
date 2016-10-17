from Process import Process
from SignalProcess import SignalProcess
import numpy as np
from tqdm import tqdm
import itertools as it
from glob import glob

signals = [SignalProcess(bp) for bp in benchmark_points] 

class myProcesses:
    def __init__(self):
        self.backgrounds = self.define_backgrounds()
        self.signals = self.define_signals()
        self.all_processes = self.signals + self.backgrounds

    def define_backgrounds(self):
        # Defining our processes
        # tt
        tt = Process('tt', 'Background')
        tt.mg5_generation_syntax = """\
        generate p p > t t~, (t > w+ b, w+ > l+ vl), (t~ > w- b~, w- > l- vl~)
        """
        tt.xsection = 17425.0 

        # tbW
        tbW = Process('tbW', 'Background')
        tbW.mg5_generation_syntax = """\
        generate p p > t w- b~ / t~, w- > l- vl~
        add process p p > t~ w+ b / t, w+ > l+ vl
        """
        tbW.xsection = 1488.0

        # bbWW
        bbWW = Process('bbWW', 'Background')
        bbWW.mg5_generation_syntax = """\
        define vv = vl vl~
        define w = w+ w-
        define ll = l+ l-
        define tt = t t~
        define bb = b b~
        generate p p > bb bb w w / tt, ( w > ll vv, w > ll vv )
        """
        bbWW.xsection = 73.0

        def set_common_bg_attributes(background):
            """ Set common background process attributes. """

            background.process_type = "Background"
            background.run_card = "Cards/run_cards/run_card.dat"
            
        for background in [tt, tbW, bbWW]:
            set_common_bg_attributes(background)
        
        return [tt, tbW, bbWW]

    def define_signals(self):
        # Check if the signal is legit - are there even any events generated?

        def isLegit(SignalProcess):
            filelist = glob(SignalProcess.output_directory+'/Events/*/*.lhco.gz')            

            if len(filelist) != 0:
                return True

        list_of_signals = filter(lambda SignalProcess: isLegit(SignalProcess), 
            [SignalProcess(combination) for combination in mass_combinations])

        return(list_of_signals)

