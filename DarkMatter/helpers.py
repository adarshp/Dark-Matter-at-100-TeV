#!usr/bin/env python
import os, re
import numpy as np
import pandas as pd
import itertools as it
import contextlib
import untangle
from tqdm import tqdm

""" Some helper functions. """

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
    """ Get SAF objects from a file. """
    convert_SAF_to_XML(filename+'.saf')
    xml_filepath = filename+'.xml'
    return (untangle.parse(xml_filepath)).root

def modify_file(filepath, line_modification_function):
    """ Modify a file in place.

    Parameters
    ----------

    filepath: str
        Path to the file to be modified.
    line_modification_function: func
        The line modification function. Takes one parameter, the line, and
        returns either the original line or a modified version of it.
    """

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

def get_benchmark_points(filename):
    df = pd.read_csv(filename, delim_whitespace=True, dtype = 'str')
    return list(df.itertuples(index=False))

