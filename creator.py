import sys
import os
import random
import string
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

	"""
    Initializes global variables and sets values based on command line arguments.
    """

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
	parser.add_option("-w", "--wlm",       dest="wlm")
	parser.add_option("-t", "--threads",   dest="threads")

	(options, args) = parser.parse_args()

	#Takes the arguments from the command-line

	if options.input_file != None:
		#sys.stdin = open(options.input_file, 'r')
		inputfile = options.input_file

	if options.outformat != None:
		outformat = options.outformat

	if options.diamond != None:
		diamond = 1

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

def fill_startbase(processes, threads, inputfile, outformat, diamond, tool, binary, database, wlm):
    """
    Fills the start base of the process with the given parameters.
    
    Parameters:
    - processes: The number of processes to be used.
    - threads: The number of threads to be used.
    - inputfile: The input file to be processed.
    - outformat: The output format of the process.
    - diamond: The diamond parameter of the process.
    - tool: The tool to be used in the process.
    - binary: The binary file to be used in the process.
    - database: The database for the process.
    - wlm: The workload manager for the process.
    """
    # Open the start.sh file in write mode
    with open("./start.sh", "w") as start:
        
        # Write the shebang line
        start.write("#!/bin/bash" + '\n\n')
        
        # Check the workload manager type
        if wlm == 'htcondor':
            pass
        elif wlm == 'slurm':
            # Open the slurm_start_base.txt file in read mode
            with open("./Bases/slurm_start_base.txt", "r") as f:
                # Write the content of slurm_start_base.txt to start.sh
                start.write(f.read())
                f.close()
        else:
            pass
        
        # Open the start_base.txt file in read mode
        with open("./Bases/start_base.txt", "r") as f:
            # Read the content of start_base.txt
            base = f.read()
            # Format the base string with the given parameters
            base = base.format(inputfile, processes, threads, outformat, diamond, tool, binary, database)
            # Write the formatted base string to start.sh
            start.write('\n' + base)
            f.close()
        
        # Close the start.sh file
        start.close()


def fill_readbase(processes, threads, outformat, diamond, tool, binary, database, wlm):
    """
    Fill the read base with the given parameters.

    Args:
        processes (int): Number of processes.
        threads (int): Number of threads.
        outformat (str): Output format.
        diamond (str): Diamond parameter.
        tool (str): Tool parameter.
        binary (str): Binary parameter.
        database (str): Database parameter.
        wlm (str): Workload manager parameter.
    """

    # Open the read.py file in write mode
    with open("./read.py", "w") as read:
        # Read the blast_additional_options.txt file and replace newlines with spaces
        with open("./Bases/blast_additional_options.txt", "r") as f:
            bao = f.read().replace("\n", " ")
            f.close()
        
        # Read the diamond_additional_options.txt file and replace newlines with spaces
        with open("./Bases/diamond_additional_options.txt", "r") as f:
            dao = f.read().replace("\n", " ")
            f.close()
        
        if wlm == 'slurm':
            # Read the slurm_partial_script_base.txt file and replace newlines with escaped newlines
            with open("./Bases/slurm_partial_script_base.txt", "r") as f:
                header = f.read().replace("\n", "\\n\" + \n\t\t\t\t\t\t \"")
                f.close()
        elif wlm == 'htcondor':
            pass
        else:
            header = ""
        
        # Read the read_base.txt file
        with open("./Bases/read_base.txt", "r") as b:
            base = b.read()
            # Format the base with the given parameters
            base = base.format(outformat, diamond, binary, database, tool, threads, processes, wlm, header, dao, bao)
            # Write the formatted base to the read.py file
            read.write(base)

        read.close()

def fill_controlscriptbase(wlm):
    """
    Generate the control_script.sh file based on the specified workload manager.

    Args:
        wlm (str): The workload manager to use (htcondor, slurm, or other).

    Returns:
        None
    """

    # Open the control_script.sh file in write mode
    with open("./control_script.sh", "w") as control:
        # Write the shebang line
        control.write("#!/bin/bash\n\n")

        if wlm == 'htcondor':
            pass

        elif wlm == 'slurm':
            # Open the slurm_controlscript_base.txt file in read mode
            with open("./Bases/slurm_controlscript_base.txt", "r") as f:
                # Write the contents of slurm_controlscript_base.txt to control_script.sh
                control.write(f.read())
                f.close()

            # Open the controlscript_base.txt file in read mode
            with open("./Bases/controlscript_base.txt", "r") as f:
                # Read the contents of controlscript_base.txt and format it with "sbatch"
                base = f.read().format("sbatch")
                # Write the formatted contents to control_script.sh
                control.write(base)
                f.close()
        else:
            # Open the controlscript_base.txt file in read mode
            with open("./Bases/controlscript_base.txt", "r") as f:
                # Read the contents of controlscript_base.txt and format it with "bash"
                base = f.read().format("bash")
                # Write the formatted contents to control_script.sh
                control.write(base)
                f.close()

        control.close()

def fill_monitor(wlm):
    """
    Generates a monitor script based on the workload manager (wlm) specified.
    If wlm is "slurm", it writes the slurm monitor commands to the file.
    If wlm is "htcondor", it does nothing.
    If wlm is "none", it removes the monitor script file.
    """

    # Open the monitor script in write mode
    with open("monitor.sh", "w") as monitor:

        # Write the shebang line
        monitor.write("#!/bin/bash\n")

        if wlm == "slurm":
            # Write the slurm monitor command and filter for "PA_proc-" jobs
            monitor.write("# Print the job details\n")
            monitor.write("echo \"             JOBID            PARTITION                           NAME     USER    STATE       TIME TIME_LIMI  NODES NODELIST(REASON)\"\n")
            monitor.write("squeue --format=\"%.18i %.20P %.30j %.8u %.8T %.10M %.9l %.6D %R\" --me | grep \"PA_proc-\"\n")

        elif wlm == "htcondor":
            pass
            # Do nothing for htcondor

        # Close the monitor script file
        monitor.close()

    if wlm == "none":
        # Remove the monitor script file
        os.remove("monitor.sh")

def fill_cancel(wlm):
    """
    Generate a cancel script based on the workload manager (wlm) type.

    Args:
        wlm (str): The type of workload manager.

    Returns:
        None
    """

    # Create a cancel script file
    with open("cancel.sh", "w") as cancel:

        # Write the shebang and description
        cancel.write("#!/bin/bash\n")
        cancel.write("# Cancel all Processes of the computation\n")

        if wlm == "slurm":
            # Cancel all processes related to the computation
            cancel.write("squeue --me | grep \"PA_proc-\" | awk '{print $1}' | xargs -n 1 scancel\n")
            
            # Append a message to the general log file
            cancel.write("echo Computation aborted >> ./general.log\n")
            cancel.write("echo '-------------------------------------------------' >> ./general.log")
        
        elif wlm == "htcondor":
            # No operation needed for HTCondor
            pass
        
        cancel.close()
    
    if wlm == "none":
        # Remove the cancel script file
        os.remove("cancel.sh")

def main():
    """
    Entry point of the program.
    """
    global processes # number of processes
    global threads   # number of threads
    global inputfile # input file
    global outformat # output format
    global diamond   # diamond
    global tool      # tool
    global binary    # binary
    global database  # database
    global wlm       # Workload Manager
    
    fill_startbase(processes, threads, inputfile, outformat, diamond, tool, binary, database, wlm)
    fill_readbase(processes, threads, outformat, diamond, tool, binary, database, wlm)
    fill_controlscriptbase(wlm)
    fill_monitor(wlm)
    fill_cancel(wlm)
    
    sp.call("chmod 777 start.sh", shell=True)  # change permission of start.sh
    sp.call("chmod 777 control_script.sh", shell=True)  # change permission of control_script.sh
    sp.call("chmod 777 read.py", shell=True)  # change permission of read.py

if __name__ == '__main__':
    init()
    sys.exit(main())
