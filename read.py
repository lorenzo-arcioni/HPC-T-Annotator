import sys
import os
import shutil
import subprocess as sp

from mpi4py import MPI
from datetime import datetime
from optparse import OptionParser

outformat  = "\"6 qseqid sseqid slen qstart qend length mismatch gapopen gaps sseq\""
inputfile  = ""
diamond    = 0
binary     = ""
database   = ""
tool       = ""


#Initialize all options and give a velue for all global variables
def init():
	
	#Declaring global variables
	global outformat    
	global inputfile 
	global diamond    
	global binary
	global tool
	global database
	
	#Defining the options
	parser = OptionParser()
	parser.add_option("-o", "--output", dest="output_file",
		          help="output file name", metavar="FILE")
	parser.add_option("-f", "--outformat", dest="outformat",
		          help="output file format", metavar="OUT_FORMAT")
	parser.add_option("-i", "--input", dest="input_file",
		          help="input file name", metavar="FILE")
	parser.add_option("-D", "--diamond", dest="diamond",
		          help="using diamond", metavar="[True, False]")
	parser.add_option("-b", "--binary", dest="binary",
		          help="binary of the tool", metavar="PATH_TO_BINARY")
	parser.add_option("-t", "--tool", dest="tool",
		          help="Blast tool", metavar="BLAST_TOOL")
	parser.add_option("-d", "--database", dest="db",
		          help="Blast database", metavar="DB_PATH")

	(options, args) = parser.parse_args()

	#Takes the arguments from the command-line
	if options.output_file != None:
		#sys.stdout = open(options.output_file, 'w') 
		pass
	if options.input_file != None:
		#sys.stdin = open(options.input_file, 'r')
		inputfile = options.input_file

	if options.outformat != None:
		outformat = options.outformat

	if options.diamond != None:
		diamond = options.diamond

	if options.binary != None:
		binary = options.binary

	if options.tool != None:
		tool = options.tool

	if options.db != None:
		database = options.db
		
def main():
	global outformat     
	global inputfile 
	global diamond    
	global binary
	global tool
	global database
	
	comm = MPI.COMM_WORLD
	size = comm.Get_size()
	rank = comm.Get_rank()

	pwd = os.getcwd() # Get current path
	generallog = os.path.join(pwd, "general.log")
	headers_file  = os.path.join(pwd, "headers.txt")
	pwd = tmpdir = os.path.join(pwd, "tmp") # Add to path the directory name

	diamond   = int(diamond) # Use or not use Diamond

	comm.Barrier() # Wait all processes
	
	if rank == 0: # dividing data into chunks
	    
	    chunks   = [[] for _ in range(size)]
	    
	    with open(headers_file) as f:
   		 keys = f.read().splitlines()
   		 
	    for i, chunk in enumerate(keys):
	    	chunks[i % size].append(chunk)
	    	
	    if os.path.exists(pwd): # If tmp already exists delete all file inside it
	    	shutil.rmtree("tmp")
	    os.mkdir("tmp")
	    	
	else:
	    chunks = None

	headers = comm.scatter(chunks, root=0) # List of sequences headers

	comm.Barrier() # Wait all processes
	
	pwd = os.path.join(pwd, str(rank))
	os.mkdir(pwd) # Every node create a folder with partials files
	outfile  = os.path.join(pwd, "blast.out")
	filename = os.path.join(pwd, "contigs.fa")

	#filename = os.path.join(pwd, "contigs.fa")
	script   = os.path.join(pwd, "script.sh")
	creator  = os.path.join(pwd, "creator.awk")
	headers_file  = os.path.join(pwd, "headers.txt")
	
	# Each node creates its custom launch script
	with open(script, 'w', encoding='utf-8') as f:   #Ogni nodo genera un suo script sbatch
		f.write("#!/bin/sh\n"+
		        "#SBATCH --job-name=PA_proc-" + str(rank) + "\n" +
		        "#SBATCH --output=tmp/" + str(rank) + "/general.out\n" +
		        "#SBATCH --error=tmp/" + str(rank) + "/general.err\n")
		        
		base = open("Bases/partial_script_base.txt", "r")
		f.write(base.read())
		base.close()		
			
		f.write("awk -f " + creator.replace(" ", "\ ") + " " + inputfile.replace(" ", "\ ") + " > " + filename.replace(" ", "\ ") + "\n")
		if diamond:
			# Get custom options from file
			additional_options = open("Bases/diamond_additional_options.txt", "r")
			options = additional_options.read()
			additional_options.close()
			
			f.write("/usr/bin/time -f \"%e\" " + binary + " " + tool + " -q " + filename + 
				                              " -d " + database + " -o " + outfile + 
				                              " -p $SLURM_CPUS_PER_TASK -f " + outformat[1:-1] + " " + options + "\n") 
		else:
			# Get custom options from file
			additional_options = open("Bases/blast_additional_options.txt", "r")
			options = additional_options.read()
			additional_options.close()
			
			f.write("/usr/bin/time -f \"%e\" " + binary + " -query " + filename + 
				                              " -db " + database + " -out " + outfile +
				                              " -num_threads $SLURM_CPUS_PER_TASK -outfmt " + outformat + " " + options +"\n")
		f.close()
		
	# Each process create its awk file
	with open(creator, 'w', encoding='utf-8') as f:
		for h in headers:
			f.write("$0 == \"" + h + "\"{print $0; while(getline == 1 && substr($1,1,1) != \">\" ){print $0}}\n")
		f.close()
	
	# Each node create its headers file
	with open(headers_file, 'w', encoding='utf-8') as f:
		f.write("\n".join(map(str, headers)))
		f.write("\n")
		f.close()
	
	sp.call("chmod 777 " + creator.replace(" ", "\ "), shell=True)	
	sp.call("chmod 777 ./tmp/" + str(rank) + "/" + "script.sh", shell=True)	#Make executable the script
	sp.call("sbatch ./tmp/" + str(rank) + "/" "script.sh", shell=True)      # Run the script
	
	comm.Barrier() # Wait all processes
	
	# Launch the control script
	if rank == 0:
		sp.call("sbatch ./script.sh", shell=True) 	

if __name__ == '__main__':
	init()
	sys.exit(main())



