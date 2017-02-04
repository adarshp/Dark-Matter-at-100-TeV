# Usage: source killjobs.sh

# for ice
# qstat -u $USER | grep $USER | cut -d " " -f1 | xargs qdel
# for Ocelote
qstat -u $USER | grep $USER | cut -d " " -f1 | cut -d "." --complement -f3 | xargs qdel
# qstat -u $USER | grep "tt" | cut -d " " -f1 | xargs qdel
