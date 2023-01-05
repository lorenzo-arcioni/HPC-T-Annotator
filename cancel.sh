#/bin/bash
#Cancel all Processes of the computation
squeue --me | grep "PA_proc-control" | awk '{print $1}' | xargs -n 1 scancel
squeue --me | grep "PA_proc-" | awk '{print $1}' | xargs -n 1 scancel
echo Calcolo annullato >> ./general.log
echo '-------------------------------------------------' >> ./general.log
