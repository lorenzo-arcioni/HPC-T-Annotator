#!/bin/bash -l
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --job-name=PA_proc-start
#SBATCH --mem=20GB
#SBATCH --time=01:00:00
#SBATCH --output=general.out
#SBATCH --error=general.err
#SBATCH -p g100_all_serial

#Loading modules
module purge
module load $anaconda_module
#source $HOME/.bashrc
source activate ./PA_env

#########################
#Create input folder with input file inside
#Translate the inputfile
#Get all the headers and put them in headers file
#########################
rm -rf ./input; mkdir input
cp "$inputfile" ./input/input.fa
inputfile=./input/input.fa
dos2unix "$inputfile"
grep ">" -i "$inputfile" > headers.txt
#########################

#Run the processes
/usr/bin/time -f "%E" mpiexec -n $processes python3 read.py -i "$inputfile" -f "$outfmt" -D $diamond -t $tool -b $binary -d $database
#mpiexec -n $processes python3 read.py -i $inputfile -f "$outfmt" -D $diamond -t $tool -b $binary -d $database
