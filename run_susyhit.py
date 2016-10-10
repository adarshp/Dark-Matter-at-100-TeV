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

    signals = processes.signals

    for signal in tqdm(signals, desc = 'Running SUSY-HIT'):
        signal.run_susyhit(susyhit_path, suspect_input_template)

if __name__ == '__main__':
    main()
