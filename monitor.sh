#!/bin/bash
echo "             JOBID            PARTITION                           NAME     USER    STATE       TIME TIME_LIMI  NODES NODELIST(REASON)"
squeue --format="%.18i %.20P %.30j %.8u %.8T %.10M %.9l %.6D %R" --me | grep "PA_proc-"
