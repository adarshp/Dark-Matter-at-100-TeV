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

def modify_prospino_main(line):
    """ Modify prospino_main.f90 to calculate the pair production cross
    section of neutral Higgsino NLSPs, and change the collider energy from
    14 TeV to 100 TeV. """

    line = line.replace('ipart1_in = 5', 'ipart1_in = 2')
    line = line.replace('ipart2_in = 7', 'ipart2_in = 3')
    line = line.replace('energy_in = 14000', 'energy_in = 100000')
    return line

def main():
    # Modify prospino main file
    modify_file('Tools/Prospino2/prospino_main.f90', modify_prospino_main)

    processes = myProcesses()
    signals = processes.signals

    for signal in tqdm(signals, desc = 'Running Prospino2', ncols = 80):
        signal.run_prospino('prospino_input/'+signal.name+'_slhaspectrum.in',
                'Tools/Prospino2', 'prospino_output')

if __name__ == '__main__':
    main()
