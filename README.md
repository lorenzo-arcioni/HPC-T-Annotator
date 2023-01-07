# HPC-Annotator
## Introduction

HPC Annotator is a parallelization tool that increases the performance of BLAST and Diamond annotation software. 
The key features are:

-   Splits the Multi-FASTA input file into more partials Multi-FASTAs.
-   Run simultaneously BLAST/Diamond sequence aligner for protein and translated DNA searches on HPC machine on partials inputs.
-   Gather and merge all partials outputs from the BLAST/Diamond and give the final result.
-   Provide a GUI that allows to generate dynamic scripts for the computation.

The software was developed to be used on large clusters with high performance and not overloaded. If the cluster where it runs is overloaded and the jobs fail to start simultaneously, there will be a considerable degradation in performance.
## Installation

The software does not require installation, but has the following requirements:

-   Python 3.8.15 (or higher)
-   PyQt5 (In your local machine, only for GUI)
-   PySide2 (In your local machine, only for GUI)
-   Anaconda
-   Slurm

If you are running on a cluster (where usually several versions are available) make sure to load a given Python version.

When using the GUI on Linux systems, the following error may be generated:
```sh
qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "" even though it was found.
This application failed to start because no Qt platform plugin could be initialized.
Reinstalling the application may fix this problem.
```
The following commands will solve.

```sh
sudo ln -s path/to/libxcb-util.so.0 /path/to/libxcb-util.so.1
```
Make sure that the Anaconda module is available on your system.

For PyQt5 and PySide2 installation you can simply:

```sh
pip install PyQt5
pip install PySide2
```

## Running
### Options for command-line execution
There are several options available
##### Mandatory options

- `-i <file.fasta>`
    Path to the query input file in multi-FASTA format. 
- `-d <database>`
    Path to the database file. 
- `-b <binary>`
    Path to the binary file (Diamond or BLAST). 
- `-t <function>`
    blastp and blastx are available.
- `-a <anaconda_module_name>`
    The name of the Anaconda module on the Slurm HPC system.

##### Other options

- `-p <number_of_processes>`
    Number of MPI processes to generate. Consider that the higher the number of processes, the more time will be needed for pre-processing. A range from 5 to 500 is recommended. Note that the number of processes must never exceed the number of sequences.
- `-f <6_BLAST_outformat>`
    The 6th tabular BLAST outformat, for example:
    ```sh
    -f "6 qseqid sseqid slen qstart qend length mismatch gapopen gaps sseq"
    ```
    Make sure that the required information is present in the database. 
- `-D`
    If we want to use the Diamond software. 

#### BLAST/Diamond further options
It is of course possible to give further options to the BLAST and Diamond software, this is done via prepared files located in the **Bases** directory.
Simply add the options in the respective file, depending on which tool you are using BLAST or Diamond.

- `blast_additional_options.txt`
- `diamond_additional_options.txt`

For example in the diamond additional options file we can insert:
```sh
--ultra-sensitive --quiet
```
It is mandatory to enter the options all on one line.

### Script configuration file
In the programme, in the **Bases** directory, there is also a file that allows the configuration of scripts that will launch BLAST/Diamond processes with customised Slurm settings, such as the estimated execution time, the threads available to the software and the RAM memory dedicated to each job. This file is: 
- `partial_script_base.txt`

### Command-line example
A command-line example using the diamond suite.
```sh
./main.sh -i ../project/assembly/slow_fast_degs_hs.fasta -b ./BANCHE_OMOLOGY/diamond -t blastx -D -a anaconda3 -d ./BANCHE_OMOLOGY/NR/nr.dmnd -p 50
```
In this case, we will divide the computation (and the input file) into 50 parts that will be processed simultaneously. In the end, the outputs of the 50 jobs will be combined into a single file.

An other example using the BLAST
```sh
./main.sh -i ../project/assembly/slow_fast_degs_hs.fasta -b /cineca/prod/opt/applications/blast+/2.12.0/binary/blastx -t blastx -a anaconda3 -d /cineca/prod/opt/applications/blast+/2.12.0/DB/nr -p 100
```

In this case we have split the computation into 100 jobs using the BLAST suite.
### Running the GUI-generated scripts
If you generated the tar archive using the GUI, simply upload the tar file into an (empty) directory of the HPC filesystem, and then execute the following command.
```sh
tar -zxf hpc_annotator.tar.gz && chmod 777 *.[sp][hy] && dos2unix *.sh
```
Once this is done, you have everything you need to manage and start the computation, so all you have to do is run:

```sh
sbatch start.sh
```
At the end of the calculation, the output will be in the **tmp** directory with the name final_blast.tsv.
### Monitoring and error checking
During the computation, its status can be monitored via the script.
```sh
./monitor.sh
```
It will return a table like this:
|JOBID|PARTITION|NAME|USER|STATE|TIME|TIME_LIMIT|NODES|NODELIST(REASON)|
| --- | ------- | -- | -- | --- | -- | -------- | --- | -------------- |
|7032348    |  g100_all_serial          |      PA_proc-control | larcioni | RUNNING   |   0:04  |  4:00:00   |   1 | login10   |
|7032347    |    g100_usr_prod          |            PA_proc-3 | larcioni | PENDING   |   0:00  |  4:00:00   |   1 | (Priority)|
|7032346    |    g100_usr_prod          |            PA_proc-2 | larcioni | PENDING   |   0:00  |  4:00:00   |   1 | (Priority)|
|7032345    |    g100_usr_prod          |            PA_proc-0 | larcioni | PENDING   |   0:00  |  4:00:00   |   1 | (Priority)|
|7032344    |    g100_usr_prod          |            PA_proc-4 | larcioni | RUNNING   |   56:30  |  4:00:00   |   1 | Node2|
|7032343    |    g100_usr_prod          |            PA_proc-1 | larcioni | RUNNING   |   1:54:43  |  4:00:00   |   1 | Node1|

It will not return the estimated end-of-calculation time as it cannot be determined a priori (because it depends on the system's workload). 

There is also a useful built-in tool for error checking that tests the input sequences, the partial inputs and outputs file and the final output, in this way we are sure that all input sequences were analysed.

An other useful script allows to check for Slurm errors:
```sh
./slurm_error_checker.sh
```
It also allows processes that resulted in an error to be re-executed.

### Log file
The software generates a log file, **general.log**, that contains all the information about all the computations performed, allowing the user to have a broad overview of how to adjust the waiting time and memory of the individual process. 
## Algorithm structure
The operation of the application, at a high level, can be summarised as follows: the master node, after analysing the input file, generates dynamic software according to the characteristics of the input, which will then be executed by the slaves nodes. Once the slaves are started, a further software will manage the control of the entire application; taking care of intervening when all the nodes have completed their computation and merging all the partial results obtained, as well as carrying out tests that, if passed, guarantee the correctness of the calculation. The control software will carry out statistics on the time taken by each node (actual and real) and on the general calculation time.

<p align="center"><img src="https://github.com/lorenzo-arcioni/HPC-Annotator/blob/main/Images/Logic-diagram.png" alt="Logic-diagram" style="height:60%; width:60%;"/></p>

## Benchmarks
Various benchmarks were run on the software, below there is a test performed on the Swiss-Prot database with the sequences of various organisms using Diamond's blastx tool.
<p align="center"><img src="https://github.com/lorenzo-arcioni/HPC-Annotator/blob/main/Images/Benchmark-SP-table.PNG" alt="Organisms times" style="height:90%; width:90%;"/></p>

## License

MIT

**Free Software, Hell Yeah!**
