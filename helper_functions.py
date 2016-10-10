#!usr/bin/env python
import os
import numpy as np
import itertools as it
import contextlib
import untangle

pbs_script = """\
#!/bin/bash
#PBS -N {process_name}_{i}
#PBS -M adarsh@email.arizona.edu
#PBS -W group_list=shufang
#PBS -q standard
#PBS -l select=1:ncpus=5:mem=23gb:localscratch=1
#PBS -l cput={cput}
#PBS -l walltime={walltime}
cd /xdisk/adarsh/Dark-Matter-at-100-TeV/Events/{process_type}s/{process_name}/{process_name}_{i}
module load python
date
pwd
rm RunWeb
./generation_script.py {nb_run}
date
echo "DONE"
exit 0"""

def convert_SAF_to_XML(filename):
    """ Converts a SAF file to XML """

    def convert_to_XML_line(line):
        """ Converts a SAF  line to XML """
        line = line.replace(' < ', ' &lt; ')
        line = line.replace(' > ', ' &gt; ')
        if line.startswith('#'):
            line = '<!-- '+line.rstrip()+' -->\n'
        return line

    with open(filename, 'r') as f:
        result = [convert_to_XML_line(line) for line in f]
    
    xml_filename = filename.split('.')[0]+'.xml'

    with open(xml_filename, 'w') as f:
        f.write('<?xml version="1.0"?>\n')
        f.write('<root>\n')
        for line in result:
            f.write(line)
        f.write('</root>\n')

def get_SAF_objects(filename):
    convert_SAF_to_XML(filename+'.saf')
    xml_filepath = filename+'.xml'
    return (untangle.parse(xml_filepath)).root

def modify_file(filepath, line_modification_function):
    with open(filepath, 'r') as f:
        lines = [line_modification_function(line) for line in f.readlines()]
    with open(filepath, 'w') as f: [f.write(line) for line in lines]

def change_directory(destination_directory):
    """ A context manager to handle temporary directory changes """
    cwd = os.getcwd()
    os.chdir(destination_directory)
    try: yield
    except: pass
    finally: os.chdir(cwd)

cd = contextlib.contextmanager(change_directory)

def razor_combinations():
    # Making a list of razor variable combinations
    m_Rs = np.arange(0.0, 4000.0, 100.0)
    m_T_Rs = np.arange(0.0, 2000.0, 100.0)
    razor_combinations = list(it.product(m_Rs, m_T_Rs))
    return razor_combinations
