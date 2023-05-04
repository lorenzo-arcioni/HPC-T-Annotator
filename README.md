# HPC-Annotator
## Introduction

HPC Annotator is a parallelization tool that increases the performance of BLAST and Diamond annotation software. 

The software was developed to be used on large clusters with high performance and not overloaded. If the cluster where it runs is overloaded and the jobs fail to start simultaneously, there will be a considerable degradation in performance.

Visit the  <a href="https://github.com/lorenzo-arcioni/HPC-Annotator/wiki">Wiki</a> page for futher informations!

## Installation
### Prerequisites

- OS: GNU Linux / Mac (though it's not tested for Mac yet - it _**should**_ work there)
- Python 3.8.15 (or higher)

If you are running on a cluster (where usually several versions are available) make sure to load a given Python 3 version.

### Get started
First, we start by cloning the repository into a folder on our filesystem on your local machine (can be also the cluster).
```sh
git clone https://github.com/lorenzo-arcioni/HPC-Annotator
```
So we extract the virtual environment.
```sh
tar -zxf hpc_annotator.tar.gz && rm hpc_annotator.tar.gz
```

The software does not require an installation process.

## Running
### Options for command-line execution
There are several options available
#### Mandatory options

- `-i <file.fasta>`
    Path to the query input file in multi-FASTA format. 
- `-d <database>`
    Path to the database file. 
- `-b <binary>`
    Path to the binary file (Diamond or BLAST). 
- `-T <function>`
    blastp and blastx are available.

#### BLAST/Diamond further options
It is of course possible to give further options to the BLAST and Diamond software, this is done via prepared files located in the **Bases** directory.
Simply add the options in the respective file, depending on which tool you are using BLAST or Diamond.

- `blast_additional_options.txt`
- `diamond_additional_options.txt`

For example in the diamond additional options file we can insert:
```sh
--ultra-sensitive --quiet
```
It is **mandatory** to enter the options all on one line.

## Execution pipeline example
After cloning the repository and extracting the TAR archive, you can proceed as follows: perform the code generation phase, upload (if necessary) the generated TAR package to the HPC machine, and then start the computation.
### Generation of code
#### Command-line generation
A command-line example using the diamond suite.
```sh
./main.sh -i /home/user/assembly/slow_fast_degs_hs.fasta -b /home/user/BANCHE_OMOLOGY/diamond -T blastx -t 48 -D -d /home/user/BANCHE_OMOLOGY/NR/nr.dmnd -p 50
```
In this case, we will divide the computation (and the input file) into 50 parts that will be processed simultaneously (with 48 threads each). In the end, the outputs of the 50 jobs will be combined into a single file.

An other example using the BLAST
```sh
./main.sh -i ../project/assembly/slow_fast_degs_hs.fasta -b /home/blast/blastx -T blastx -t 48 -d /home/user/DB/nr -p 100
```

In this case we have split the computation into 100 jobs using the BLAST suite.

#### Interface generation

### Execution on HPC machine
So we extract the generated code.
```sh
tar -zxf hpc_annotator.tar && rm hpc_annotator.tar
```
Once this is done, you have everything you need to manage and start the computation, so all you have to do is run (if you are on Slurm):

```sh
sbatch start.sh
```
Or (if you are on HTCondor):
```sh
condor_submit start.sh
```

At the end of the calculation, the output will be in the **tmp** directory with the name **final_blast.tsv**.

## License

**Free Software, Yeah!**
