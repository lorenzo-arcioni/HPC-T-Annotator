#!/bin/bash
#Main script

#Use it to automate the running of the start.sh
usage="$(basename "$0") -i inputfile [-h] [-p number_of_processes] [-f blastx_out_fotmat] [-d database path] [-a anaconda slurm module name] [-D] [-t used tools] [-b binary of executable] -- parallel annotation application with Blast/Diamond tool"

outfmt="\"6 qseqid sseqid slen qstart qend length mismatch gapopen gaps sseq\""

diamond=0

while getopts ':i:hDp:f:b:t:d:a:' option;
do
    case "${option}" in
        h) echo $usage
           exit 0;;
        i) inputfile=$OPTARG;;
        f) outfmt="\"${OPTARG}\"";;
        D) diamond=1;;
        p) processes=$OPTARG;;
        b) binary=$OPTARG;;
        t) tool=$OPTARG;;
        d) database=$OPTARG;;
        a) anaconda_module=$OPTARG;;
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

if [ -z "$binary" ]
then
	echo "Insert some binary path" >&2
	echo $usage
	exit 2
fi

if [ -z "$tool" ] && [ $diamond == 1 ]
then
	echo "Insert the tool" >&2
	echo $usage
	exit 2
fi

if [ -z "$database" ]
then
	echo "Insert the database" >&2
	echo $usage
	exit 2
fi

if [ "$tool" != "blastx" -a "$tool" != "blastp" ]
then
	echo "Only blastx and blastp are supported in this version, please insert one of this tools" >&2
	echo $usage
	exit 2
fi

#Calculate the number of sequences
sequences=$(grep ">" -i "$inputfile" -c)
if [ -z "$processes" ]
then
	processes=$sequences
fi

if [ $processes -gt $sequences ]
then
	echo "The number of processes must be lower then the sequences number" >&2
	exit 3
fi

if [ -z "$anaconda_module" ]
then
	anaconda_module="anaconda3"
fi

echo "Current settings"
echo
echo Total processes: $processes
echo Sequences: $sequences
echo input file: $inputfile
echo output format: $outfmt
echo tool: $tool
echo database: $database
echo binary path: $binary
echo anaconda module: $anaconda_module
if [ $diamond == 1 ]
then
	echo "Blast with Diamond"
fi
echo
echo "Continue? (y/n)"
read choice

if [ "$choice" = "y" ]
then
	#export processes=$processes inputfile=$inputfile outfmt="$outfmt" diamond=$diamond binary=$binary database=$database anaconda_module=$anaconda_module tool=$tool && ./start.sh	
	sbatch --export=ALL,processes=$processes,inputfile=$inputfile,outfmt="$outfmt",diamond=$diamond,tool=$tool,binary=$binary,database=$database,anaconda_module=$anaconda_module start.sh
	
	#Updating log file
	echo "Starting timestamp#""$(date +'%Y-%m-%d %H:%M:%S')" >> ./general.log
	echo Input file: $inputfile >> ./general.log
	echo Processes: $processes >> ./general.log
	echo Out-format: $outfmt >> ./general.log
	[ $diamond -eq 1 ] && echo "Diamond: yes" >> ./general.log || echo "Diamond: no" >> ./general.log
	echo Tool: $tool >> ./general.log
	echo Binary: $binary >> ./general.log
	echo Database: $database >> ./general.log
	echo Anaconda module: $anaconda_module >> ./general.log
	cat ./Bases/script_base.txt >> ./general.log
	echo Sequences: $sequences >> ./general.log
fi


