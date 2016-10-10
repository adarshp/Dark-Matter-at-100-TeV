#!/usr/bin/env python

import sys
import os
import contextlib
from helpers import cd, modify_file
from tqdm import tqdm
from templates import *
import logging
from myProcesses import myProcesses


# Set up environment variables
# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(levelname)s: %(message)s')

def main():
    processes = myProcesses()

    susyhit_path = "Tools/susyhit"
    relative_mg5_path = "Tools/mg5"

    signals = processes.signals
    for signal in tqdm(signals, desc='Creating MG5 directories'):
        signal.create_mg5_process_directory(relative_mg5_path)

    """
    for signal in tqdm(signals, desc = 'Copying cards'):
        signal.copy_param_card(susyhit_path+'/susyhit_slha.out')
        signal.copy_delphes_card()
        signal.copy_run_card()
        """

if __name__ == '__main__':
    main()
