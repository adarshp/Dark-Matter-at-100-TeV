#!/usr/bin/env python

from helper_functions import cd, modify_file
from tqdm import tqdm
import logging
from myProcesses import myProcesses

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def main():
    processes = myProcesses()

    # mySignals = filter(lambda signal: signal.higgsino_mass > 2000, 
            # processes.signals)
    print('Generating 50000 events for selected mass combinations')

    for signal in tqdm(processes.signals, ncols = 80):
        tqdm.write('Generating events for '+signal.name)
        signal.copy_param_card()
        signal.copy_delphes_card()
        signal.copy_run_card()
        signal.generate_events(50000)

if __name__ == '__main__':
    main()
