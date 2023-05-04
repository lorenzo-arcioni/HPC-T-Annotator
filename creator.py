import sys
import os
from optparse import OptionParser
import subprocess as sp

outformat  = "\"6 qseqid sseqid slen qstart qend length mismatch gapopen gaps sseq\""
inputfile  = None
diamond    = 0
binary     = None
database   = None
tool       = None
wlm        = None
processes  = 1
threads    = 1

#Initialize all options and give a velue for all global variables
def init():

	#Declaring global variables
	global processes
	global threads
	global inputfile
	global outformat
	global diamond
	global tool
	global binary
	global database
	global wlm

	#Defining the options
	parser = OptionParser()

	parser.add_option("-p", "--processes", dest="processes")
	parser.add_option("-f", "--outformat", dest="outformat")
	parser.add_option("-i", "--input",     dest="input_file")
	parser.add_option("-D", "--diamond",   dest="diamond")
	parser.add_option("-b", "--binary",    dest="binary")
	parser.add_option("-T", "--tool",      dest="tool")
	parser.add_option("-d", "--database",  dest="db")
	parser.add_option("-w", "--wlm",  dest="wlm")
	parser.add_option("-t", "--threads",   dest="threads")


	(options, args) = parser.parse_args()

	#Takes the arguments from the command-line

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

	if options.wlm != None:
		wlm = options.wlm

	if options.threads != None:
		threads = options.threads

	if options.processes != None:
		processes = options.processes

def fill_startbase():
	global processes
	global threads
	global inputfile
	global outformat
	global diamond
	global tool
	global binary
	global database

	with open("./start.sh", "w") as start:

		start.write("#!/bin/bash" + '\n\n')

		if wlm == 'htcondor':
			pass

		elif wlm == 'slurm':
			
			with open("./Bases/slurm_start_base.txt", "r") as f:
				start.write(f.read())
				f.close()
		else:
			pass

		with open("./Bases/start_base.txt", "r") as f:
			base = f.read()
			base = base.format(inputfile, processes, threads, outformat, diamond, tool, binary, database)
			start.write('\n' + base)
			f.close()

	start.close()

def fill_readbase():
	global processes
	global threads
	global inputfile
	global outformat
	global diamond
	global tool
	global binary
	global database

	with open("./read.py", "w") as read:

		with open("./Bases/blast_additional_options.txt", "r") as f:
			bao = f.read().replace("\n", "")
			f.close()
		
		with open("./Bases/diamond_additional_options.txt", "r") as f:
			dao = f.read().replace("\n", "")
			f.close()
		
		if wlm == 'slurm':
			with open("./Bases/slurm_partial_script_base.txt", "r") as f:
				header = f.read().replace("\n", "\\n\" + \n\t\t\t\t\t\t \"")
				f.close()

		elif wlm == 'htcondor':
			pass

		else:
			header = ""
		
		with open("./Bases/read_base.txt", "r") as b:
			base = b.read()
			base = base.format(outformat, diamond, binary, database, tool, threads, processes, wlm, header, dao, bao)
			read.write(base)

		read.close()

def fill_controlscriptbase():
	global processes
	global threads
	global inputfile
	global outformat
	global diamond
	global tool
	global binary
	global database
	global wlm

	with open("./control_script.sh", "w") as control:

		control.write("#!/bin/bash" + '\n\n')

		if wlm == 'htcondor':
			pass

		elif wlm == 'slurm':
			
			with open("./Bases/slurm_controlscript_base.txt", "r") as f:
				control.write(f.read())
				f.close()

			with open("./Bases/controlscript_base.txt", "r") as f:
				base = f.read().format("sbatch")
				control.write(base)
				f.close()
		else:

			with open("./Bases/controlscript_base.txt", "r") as f:
				base = f.read().format("bash")
				control.write(base)
				f.close()

		control.close()

def fill_monitor():
	global wlm

	with open("monitor.sh", "w") as monitor:

		monitor.write("#!/bin/bash\n")

		if wlm == "slurm":
			monitor.write("echo \"             JOBID            PARTITION                           NAME     USER    STATE       TIME TIME_LIMI  NODES NODELIST(REASON)\"\n")
			monitor.write("squeue --format=\"%.18i %.20P %.30j %.8u %.8T %.10M %.9l %.6D %R\" --me | grep \"PA_proc-\"\n")
		
		elif wlm == "htcondor":
			pass

		monitor.close()
	
	if wlm == "none":

		os.remove("monitor.sh")



def fill_cancel():
	global wlm

	with open("cancel.sh", "w") as cancel:

		cancel.write("#!/bin/bash\n")
		cancel.write("#Cancel all Processes of the computation\n")

		if wlm == "slurm":
			cancel.write("squeue --me | grep \"PA_proc-\" | awk '{print $1}' | xargs -n 1 scancel\n")
			cancel.write("echo Computation aborted >> ./general.log\n")
			cancel.write("echo '-------------------------------------------------' >> ./general.log")
		
		elif wlm == "htcondor":
			pass
		
		cancel.close()
	
	print(wlm)

	if wlm == "none":

		os.remove("cancel.sh")


def main():
	global processes
	global threads
	global inputfile
	global outformat
	global diamond
	global tool
	global binary
	global database
	global wlm

	fill_startbase()
	fill_readbase()
	fill_controlscriptbase()
	fill_monitor()
	fill_cancel()

	sp.call("chmod 777 start.sh", shell=True)
	sp.call("chmod 777 control_script.sh", shell=True)
	sp.call("chmod 777 read.py", shell=True)

if __name__ == '__main__':
    init()
    sys.exit(main())
