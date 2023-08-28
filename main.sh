#!/bin/bash
#Main script

#Use it to automate the running of the start.sh
usage="$(basename "$0") -i inputfile [-h] [-p number_of_processes] \
[-f blastx_out_fotmat] [-d database path] [-D] [--slurm] [--htcondor]\
[-T used tools] [-b binary of executable] [-t threads]\
-- parallel annotation application with Blast/Diamond tool"

outfmt="\"6 qseqid sseqid slen qstart qend length mismatch gapopen gaps sseq\""

diamond=0
wlm='none'

while getopts ':i:hDp:f:b:t:T:d:-:' option;
do
    case "${option}" in
        h) echo $usage
           exit 0;;
        i) inputfile=$OPTARG;;
        f) outfmt="\"${OPTARG}\"";;
        D) diamond=1;;
        p) processes=$OPTARG;;
		t) threads=$OPTARG;;
        b) binary=$OPTARG;;
        T) tool=$OPTARG;;
        d) database=$OPTARG;;

		-)
			case "${OPTARG}" in
				slurm)
				wlm='slurm'
				;;
				htcondor)
				wlm='htcondor'
				;;
				* )
				echo printf "illegal option: -%s\n" "$OPTARG" >&2
					echo "$usage" >&2
					exit 1
				;;
			esac
			;;

        :) printf "missing argument for -%s\n" "$OPTARG" >&2
			echo "$usage" >&2
	   		exit 1;;
		?) printf "illegal option: -%s\n" "$OPTARG" >&2
            echo "$usage" >&2
            exit 1;;
		
    esac
done

if [ -z "$inputfile" ]
then
	echo "Insert an input file" >&2
	echo $usage
	exit 2
fi

if [ -z "$threads" ]
then
	echo "Insert the number of threads" >&2
	echo $usage
	exit 2
fi

if [ -z "$binary" ]
then
	echo "Insert some binary path" >&2
	echo $usage
	exit 2
fi

if [ -z "$tool" ] && [ $diamond == 1 ]
then
	echo "Insert the tool (blastx or blastp)" >&2
	echo $usage
	exit 2
fi

if [ -z "$database" ]
then
	echo "Insert the database path" >&2
	echo $usage
	exit 2
fi

if [ "$tool" != "blastx" -a "$tool" != "blastp" ]
then
	echo "Only blastx and blastp are supported in this version, please insert one of this tools." >&2
	echo $usage
	exit 2
fi

#Calculate the number of sequences
sequences=$(grep ">" -i "$inputfile" -c)
if [ -z "$processes" ]
then
	echo "Insert the number of processes (must be less or equal to the number of sequences in the input file)" >&2
	echo $usage
	exit 2
fi

if [ $processes -gt $sequences ]
then
	echo "The number of processes must be lower then the sequences number" >&2
	exit 3
fi

echo "Current settings"
echo
echo Total processes: $processes
echo Sequences: $sequences
echo Input file: $inputfile
echo Output format: $outfmt
echo Tool: $tool
echo Threads: $threads
echo Database: $database
echo Binary path: $binary
echo Workload manager: $wlm

if [ $diamond == 1 ]
then
	echo "Blast with Diamond"
fi

echo
echo "Continue? (y/n)"
read choice

if [ "$choice" = "y" ]
then
	python3 creator.py -p $processes -i "$inputfile" -f "$outfmt" -T $tool -t $threads -d "$database" -b "$binary" -w "$wlm" -D $diamond

	echo "All codes are correctly generated!"
	echo "Do you want to: (enter the number choice and press ENTER)"
	echo "1) Exec your code rigth now (on this machine)"
	echo "2) Generate tar file to upload on a remote machine"
	echo "3) Exit"
	read choice

	if [ "$choice" = "1" ]; then
			case "$wlm" in
				slurm)
				sbatch --export=ALL,processes=$processes,threads=$threads,inputfile=$inputfile,outfmt="$outfmt",diamond=$diamond,tool=$tool,binary=$binary,database=$database start.sh
				;;
				htcondor)
				echo "Work in progress!!"
				;;
				none)
				export processes=$processes threads=$threads inputfile=$inputfile outfmt="$outfmt" diamond=$diamond binary=$binary database=$database tool=$tool && ./start.sh
				;;
			esac
	else if [ "$choice" = "2" ]; then
		case "$wlm" in
			slurm)
			tar -cf hpc-t-annotator.tar read.py start.sh time_calculator.py control_script.sh splitter.py
			;;
			htcondor)
			echo "Work in progress!!"
			echo "This choice is not available."
			;;
			none)
			tar -cf hpc-t-annotator.tar read.py start.sh time_calculator.py control_script.sh splitter.py
			;;
		esac 
		rm  read.py start.sh control_script.sh

		fi
		
	fi

fi
