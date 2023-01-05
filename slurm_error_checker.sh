#Get all errors from all processes
jobs=$(grep "slurm" -i ./tmp/*/general.err 2>/dev/null)

#If there are some errors
if [ "$jobs" != "" ]
then
	#Print all errors detected
	for y in "$jobs";
	do
		echo "$y"
	done
	echo "re-run these jobs? (y/n)"
	read choice

	if [ "$choice" = "y" ]
	then
		#Rerun all processes with errors
	        for x in $(grep "slurm" -i ./tmp/*/general.err 2>/dev/null | grep -o  "./.*/.*/" 2>/dev/null);
		do
			sbatch "$x""script.sh"
		done
	fi
	echo "re-run the control script? (y/n)"
	read choice

	if [ "$choice" = "y" ]
	then
		sbatch script.sh
	fi
else
	echo No errors detected!
fi
