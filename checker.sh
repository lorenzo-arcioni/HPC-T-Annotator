#!/bin/bash

x=0 #input file dimension
y=0 #output file dimension
h=0 #errors counter

#For each directory in ./tmp gather the partials out/in file dimensions 
#And check for all sequences in inputfile if they are in headers file
for d in ./tmp/*/ ; 
	do
		x=$(($x + $(wc -c < ${d}contigs.fa)))
		y=$(($y + $(wc -c < ${d}blast.out)))
	done
	
echo -n Test on input ....
if [ $x -eq $(wc -c < $1) ]
	then
		echo OK $x
	else
		echo Wrong
		echo Given $x ... expected $(wc -c < $1)
fi

echo -n Test on output ....
if [ $y -eq $(tail -n +2 ./tmp/final_blast.tsv | wc -c) ]
	then
		echo OK $y
	else
		echo Wrong
		echo Given $y ... expected $(wc -c < ./tmp/final_blast.tsv)
fi


