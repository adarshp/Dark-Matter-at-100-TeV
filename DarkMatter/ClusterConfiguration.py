class ClusterConfiguration(object):
    """A template for creating a cluster configuration.

    Attributes
    ----------
    username : str
        Your username. For University of Arizona users, this is your NetID.
    email : str
        Your email, used to send notifications when a cluster job begins and
        ends.
    group_list : str
        The group you belong to. For UA users, this should be the name of
        your PI in lowercase.
    """
    def __init__(self, username, email, group_list, pbs_script_template):
        self.username = username
        self.email = email
        self.group_list = group_list
        self.pbs_script_template = pbs_script_template

myClusterConfig = ClusterConfiguration(
  username = 'adarsh',
  email = 'adarsh@email.arizona.edu',
  group_list = 'shufang',
  pbs_script_template = """\
#!/bin/bash
#PBS -m bea
#PBS -N {jobname}
#PBS -M {email}
#PBS -W group_list={group_list}
#PBS -q standard
#PBS -l jobtype=htc_only
#PBS -l select=1:ncpus=5:mem=23gb
#PBS -l cput=0:{cput}:0
#PBS -l walltime=0:{walltime}:0
cd /extra/{username}/ExoticHiggs/{mg5_process_dir}
for i in {{1..{nruns}}}
do
  ./bin/generate_events -f --laststep=delphes
  ./bin/madevent remove all parton -f
  ./bin/madevent remove all pythia -f
  rm -rf Events/run_*/tag_*_delphes_events.root
done
echo "DONE"
exit 0"""
)
""" This is the actual configuration for the cluster, that you must
modify before using the package to generate events on the cluster."""
