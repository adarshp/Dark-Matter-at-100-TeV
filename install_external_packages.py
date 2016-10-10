#!/usr/bin/env python

""" This module downloads, sets up and links some of the external packages
needed for your analysis """

import subprocess as sp
from helper_functions import cd, modify_file
import os
import shutil
import contextlib
import fileinput
import logging

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(levelname)s: %(message)s')

def install_delphes():
    """
    Downloads Delphes into the current directory, and compiles it.

    Parameters:
    -----------
    directory : string
        The directory into which Delphes will be cloned and installed.
    
    """
    if os.path.exists('delphes'): shutil.rmtree('delphes')
    sp.call(['git', 'clone', 'https://github.com/delphes/delphes.git'])
    with cd('delphes'):
        sp.call('./configure; make -j 8', shell = True)


def install_madgraph():
    """
    Downloads and installs MadGraph5 to the current directory.

    Parameters:
    -----------
    directory : string
        The directory into which MadGraph5 will be cloned and installed.
    """

    if os.path.exists('mg5'): shutil.rmtree('mg5')

    # Download MadGraph 5
    print("Downloading MadGraph5...")
    sp.call(['wget',
    'https://launchpad.net/mg5amcnlo/2.0/2.4.x/+download/MG5_aMC_v2.4.3.tar.gz'])
    sp.call(['tar','-zxvf','MG5_aMC_v2.4.3.tar.gz'])
    os.rename('MG5_aMC_v2_4_3','mg5')

    # Delete the tarball
    os.remove('MG5_aMC_v2.4.3.tar.gz')

    with cd('mg5'):
        # Write a script to install Pythia
        with open('install_pythia.cmd','w') as f:
            f.write('install pythia-pgs\n')

        # Run MG5 with the commands to install Pythia and Delphes
        sp.call(['./bin/mg5_aMC','install_pythia.cmd'])

def download_madanalysis():
    """
    Downloads and extracts MadAnalysis5 to the current directory.

    Parameters:
    -----------
    directory : string
        The directory into which MadAnalysis5 will be cloned and installed.

    """

    # Download MadAnalysis5
    if os.path.exists('madanalysis5'): shutil.rmtree('madanalysis5')

    try:
        sp.call(['wget',
        'https://launchpad.net/madanalysis5/trunk/v1.4/+download/MadAnalysis5_v1.4.tar.gz'])
    except:
        print("Dowloading MadAnalysis5 v1.4 failed \
        - check https://launchpad.net/madanalysis5 for a newer version.")
    sp.call(['tar','-zxvf','MadAnalysis5_v1.4.tar.gz'])
    os.remove('MadAnalysis5_v1.4.tar.gz')
    # Modify the LHCOReader file

    with cd('madanalysis5/tools/SampleAnalyzer/Process/Reader'):
        helpers.modify_file('LHCOReader.cpp',
                            lambda line: line.replace('tmp ==2', 'tmp == 3'))
def specify_delphes_path(line):
    """ A helper function to check if a line starts with a delphes option, 
    to specify the correct Delphes path
    
    Parameters:
    -----------
    line : string
        The line to process
    delphes_path : string
        The relative path of the Delphes directory from the package directory
    """
    if line.startswith('# delphes_'):
        words = line.split(' ')
        if words[1] in ['delphes_includes', 'delphes_libs', 'delphes_path']:
            delphes_path = os.getcwd() + '/delphes'
            line = '{} = {}\n'.format(words[1], delphes_path)
    return line

def link_package_with_delphes(package_name, package_path):
    """ Links the specified package with Delphes 
    
    Parameters
    ----------
    package_name : string
        The name of the package. Available options: madgraph, madanalysis
    package_path : string
        Relative path to the package
    delphes_path : string
        Relative path to Delphes (from the package directory)
    """

    if package_name == 'madgraph': 
        configfile = 'input/mg5_configuration.txt'
    elif package_name == 'madanalysis': 
        configfile = 'madanalysis/input/installation_options.dat'
    else: print('package_name must be \'madgraph\' or \'madanalysis\'.')

    filepath = package_path + configfile
    helpers.modify_file(filepath, specify_delphes_path)

def install_prospino():
    """ Installs Prospino to the current directory """
    if os.path.exists('Prospino2'): shutil.rmtree('Prospino2')
    sp.call(['git', 'clone', 'https://github.com/HEPcodes/Prospino2'])
    
    # Modify Makefile to facilitate easier recompilation
    helpers.modify_file('Prospino2/Makefile',
                        lambda l: l.replace('rm -i', 'rm -f'))
    with cd('Prospino2'):
        sp.call('make')

def install_susyhit():
    """ Installs SUSY-HIT to the current directory """
    if os.path.exists('susyhit'): shutil.rmtree('susyhit')
    os.makedirs('susyhit')
    with cd('susyhit'):
        sp.call(['wget', 'https://www.itp.kit.edu/~maggie/SUSY-HIT/susyhit.tar.gz'])
        sp.call(['tar', '-zxvf', 'susyhit.tar.gz'])
        os.remove('susyhit.tar.gz')
        sp.call('make')

def main(install_directory):
    """ 
    Installs Delphes, MadGraph5 and MadAnalysis5 to the specified directory.
    
    Parameters
    ----------
    install_directory : string
        Name of the directory to install the packages to. If it does not exist
        already, it will be created.
    """

    if not os.path.exists(install_directory): 
        os.makedirs(install_directory)

    with cd(install_directory):
        logging.info('Installing Delphes ...')
        install_delphes()
        logging.info('Installing MadGraph5 ...')
        install_madgraph()
        logging.info('Linking MadGraph5 with Delphes ... ')
        link_package_with_delphes('madgraph', 'mg5/')
        logging.info('Downloading MadAnalysis5 ...')
        download_madanalysis()
        logging.info('Linking MadAnalysis5 with Delphes ... ')
        link_package_with_delphes('madanalysis', 'madanalysis5/')
        logging.info('Starting up MadAnalysis5 for the first time to compile'
                        + ' SampleAnalyzer libraries...')
        sp.call('./madanalysis5/bin/ma5')
        logging.info("Downloading and installing SUSY-HIT")
        install_susyhit()
        logging.info("Downloading and installing Prospino2")
        install_prospino()

if __name__ == '__main__':
    main('Tools')
