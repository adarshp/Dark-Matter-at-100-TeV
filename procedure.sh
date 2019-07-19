# Procedure to run the analysis:

# Create signal directory
source create_signal_dir.sh

# set up MA5 environment variables.
source setup.sh

# Run the preselection for signals and backgrounds. 
./cut_n_count.py --preselect_signals
qsub pbs_scripts/preselect_backgrounds.pbs

# Run cut and count analyses for signals and backgrounds
qsub pbs_scripts/cc_scan_signals.pbs
qsub pbs_scripts/cc_scan_backgrounds.pbs

# Collect CC results
qsub pbs_scripts/cc_scan_results.pbs

# Make representative Cut and count cut flow table for paper 
./collect_cc_results --cc_rep

# Run BDT analysis for signals and backgrounds
# Make background feature arrays:
cd BackgroundFeatureArrays/Build
analyze.sh
cd -

# Make signal feature arrays:
./make_feature_arrays.py --signals

# Run BDT scan
qsub pbs_scripts/bdt_scan.pbs

# Collect BDT results.
./make_contour_plot.py --collect
./make_contour_plot.py --combined
