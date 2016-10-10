from process import *

# Making a dictionary with process names and types
processes = {
  "proc_1": "Signal",
  "tt": "Background",
  "tbW": "Background",
  "bbWW": "Background"
}

# Making a dictionary to map names to members of the 'process' class
process = {name: process(name, type) for name, type in processes.iteritems()}

[process[name].copy_cards() for name in ['proc_1', 'tt', 'tbW', 'bbWW']]
