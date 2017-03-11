#!/bin/bash

# Build input file list
ls -f /extra/adarsh/Events/Backgrounds/$1/bbllvv/100_TeV/*/Events/run_*/*.lhco.gz > ../Input/$1

# Delete previous analysis directory
rm -rf ../Output/$1

# Run analysis
./MadAnalysis5job ../Input/$1
