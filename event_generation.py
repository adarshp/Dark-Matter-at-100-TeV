#!/usr/bin/env python
from __future__ import division
import os
import sys
sys.path.insert(0, '/extra/adarsh/clusterpheno')
from clusterpheno.helpers import cd, modify_file, do_parallel
import subprocess as sp
import shutil as sh
from myProcesses import signals
from tqdm import tqdm
from ConfigParser import SafeConfigParser

if __name__ == '__main__':
    mg5_path = '/extra/adarsh/Tools/mg5/'
    write_madevent_scripts(signals)
    # signals[0].create_directory(mg5_path)
    # do_parallel(lambda x: x.create_directory(mg5_path),signals,12)
    # do_parallel(copy_cards,signals, 2)
    # parser = SafeConfigParser()
    # parser.read('config.ini')
    # write_pbs_scripts(signals, parser, 20)
    # map(lambda x: x.generate_events(), tqdm(signals, desc = "submitting PBS jobs"))
