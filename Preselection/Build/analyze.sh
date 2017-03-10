ls -f Events/Signals/H1H2/bbll_MET/100_TeV/$1/Events/run_*/*.lhco.gz > ../Input/$1
./MadAnalysis5job ../Input/$1
