#!/usr/bin/env python

from __future__ import division
import os
import sys
sys.path.insert(0, '/extra/adarsh/clusterpheno')
from clusterpheno.helpers import *
import subprocess as sp
import shutil as sh
from myProcesses import signals, backgrounds
from tqdm import tqdm
from ConfigParser import SafeConfigParser
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from glob import glob
import random
import multiprocessing as mp
from BDTClassifier import BDTClassifier

import pandas as pd
from myProcesses import signals
from sklearn.model_selection import train_test_split
def create_template_analysis(parser):
    sp.call(['./'+parser.get('Tools', 'relative_ma5_path')+'/bin/ma5', '-E',
             'MakeFeatureArray', 'Analysis'])

def main():
# mySignal = filter(lambda x: x.mH == 2000 and x.mB == 25, signals)[0]
# df = pd.read_csv(mySignal.directory+'/MakeFeatureArray/Output/feature_array.txt')
# train_set, test_set = train_test_split(df)

    classifier = BDTClassifier(signals[0])
    make_bdt_response_histo(classifier)
    # do_parallel(analyze,signals[0:12],5)

if __name__ == '__main__':
    main()
