from process import *
import subprocess, glob

# Making a dictionary with process names and types
processes = {
  "proc_1": "Signal",
  "tt": "Background",
  "tbW": "Background",
  "bbWW": "Background"
}

# Making a dictionary to map names to members of the 'process' class
process = {name: process(name, type) for name, type in processes.iteritems()}

[process[name].write_pbs_submit_scripts(70) for name in ['tt', 'tbW', 'bbWW']]
process['proc_1'].write_pbs_submit_scripts(3)

# Submit the jobs to the cluster
[subprocess.call(['qsub', filename]) for filename in \
  glob.glob('event_generation/pbs_submission_scripts/*.pbs')]
