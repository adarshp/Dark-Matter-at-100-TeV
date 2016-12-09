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

def make_feature_array(signal):
    with cd(signal.directory+'/MakeFeatureArray/Build'):
        sp.call('./analyze.sh')

def main():
    do_parallel(make_feature_array,signals[3:5])

if __name__ == '__main__':
    main()
