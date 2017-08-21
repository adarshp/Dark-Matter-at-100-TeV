#!/bin/bash

# Build input file list
ls -f /rsgrps/shufang/$1/Events/run_*/*.lhco.gz > ../Input/$1

# Delete previous analysis directory
rm -rf ../Output/$1

# Run analysis
./MadAnalysis5job ../Input/$1
