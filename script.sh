#!/bin/bash
#SBATCH --job-name=PA_proc-control
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --threads-per-core=1
#SBATCH --mem=10GB
#SBATCH --time=04:00:00
#SBATCH --output=general_script.out
#SBATCH --error=general_script.err
#SBATCH -p g100_all_serial
#SBATCH --mail-type=END
#SBATCH --mail-user=lorenzo.arcioni2000@gmail.com

start_time=$(date +%s)

#Meanwhile there are still process running
while [ $(squeue --format="%.18i %.20P %.30j %.8u %.8T %.10M %.9l %.6D %R" --me | grep -E "PA_proc-[0-9]+" | wc -l) != 0 ]
do
	end_time=$(date +%s)
	
	#If my running time > 3 hours
	if [ $(( end_time - start_time )) -gt 10800 ]
		then
			#Launch my clone
			sbatch ./script.sh
			exit 0
	fi
	sleep 5
done

#For each directory (process)
for d in ./tmp/*/ ; 
	do
		#Append partial output to the main aoutput
		cat ${d}blast.out >> ./tmp/final_blast.tsv
		
		#Get statistics data
		cat ${d}general.err | tr "\n" , >> ./errors_and_time.csv
		echo $(ls -l ${d}contigs.fa | cut -d' ' -f5) >> ./errors_and_time.csv
	done
#Calculate time
python3 time_calculator.py >> ./general.log  

#Update log files
date1=$(grep "Starting timestamp#" -i ./general.log | tail -1 | cut -d"#" -f 2)
date2=$(date +'%Y-%m-%d %H:%M:%S')
echo "Ending timestamp#"$date2 >> ./general.log
diff=$(($(date -d "$date2" +'%s') - $(date -d "$date1" +'%s')))
echo "Total elapsed time: "$(date -d @$diff -u +%H:%M:%S) >> ./general.log
#./checker.sh input/input.fa > ./errors.log
date -u -d @$(($(date -d "$date2" '+%s') - $(date -d "$date1" '+%s'))) '+%T'
echo '-------------------------------------------------' >> ./general.log
#mail -s 'Computazione ultimata' lorenzo.arcioni2000@gmail.com <<< $(tail -8 ./general.log)$'\n'$(cat errors.log)

