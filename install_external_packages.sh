#!/usr/bin/env bash

# Install python packages
pip install -r requirements.txt

# Make a Tools directory
mkdir Tools; cd Tools

# Install MadGraph5 v2.4.3
wget https://launchpad.net/mg5amcnlo/2.0/2.4.x/+download/MG5_aMC_v2.4.3.tar.gz
tar -zxvf MG5_aMC_v2.4.3.tar.gz
rm MG5_aMC_v2.4.3.tar.gz; mv MG5_aMC_v2_4_3 mg5; cd mg5
echo install pythia-pgs >> install_pythia_delphes.cmd
echo install Delphes  >> install_pythia_delphes.cmd
./bin/mg5_aMC install_pythia_delphes.cmd; cd ../

# Install SUSY-HIT
mkdir susyhit; cd susyhit
wget https://www.itp.kit.edu/~maggie/SUSY-HIT/susyhit.tar.gz 
tar -zxvf susyhit.tar.gz
rm susyhit.tar.gz; make; cd ../

# Install Prospino
git clone https://github.com/HEPcodes/Prospino2
sed -i 's/rm -i/rm -f/g' Prospino2/Makefile
cd Prospino2; make; cd ../

# Install MadAnalysis5
wget https://launchpad.net/madanalysis5/trunk/v1.4/+download/MadAnalysis5_v1.4.tar.gz
tar -zxvf MadAnalysis5_v1.4.tar.gz; rm MadAnalysis5_v1.4.tar.gz; cd madanalysis5
sed -i 's/tmp ==2/tmp == 3/g' madanalysis5/tools/SampleAnalyzer/Process/Reader/LHCOReader.cpp
echo "install delphes" >> install_delphes.cmd
./bin/ma5 --script=install_delphes.cmd
