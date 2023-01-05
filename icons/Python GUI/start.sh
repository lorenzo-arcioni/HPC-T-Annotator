#!/bin/bash -l
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --mem=20GB
#SBATCH --time=04:00:00
#SBATCH --output=general.out
#SBATCH --error=general.err
#SBATCH --account=Paolo
#SBATCH -p partition_paolo
module purge
module load anaconda3
source /g100/home/userexternal/larcioni/.bashrc
source activate ./envs
/usr/bin/time -f "%E" mpiexec -n 13 python3 read.py -i input_paolo -f "6 format_paolo" -d 0