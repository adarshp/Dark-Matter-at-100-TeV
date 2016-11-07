#!/usr/bin/env python

# A script to kill all your PBS jobs on the University of Arizona cluster.
# Usage: python killjobs.py

import os
import subprocess as sp
from tqdm import tqdm

def main():
    username = os.getcwd().split('/')[5]
    output = sp.check_output(['qstat', '-u', username])
    lines = output.split('\n')[5:]
    jobs = [words[0] for words in [line.split() for line in lines] if len(words) > 1]
    for job in tqdm(jobs, desc = "Deleting PBS jobs"):
        sp.call(['qdel', job])

if __name__ == '__main__':
    main()
