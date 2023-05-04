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

### Command-line example
A command-line example using the diamond suite.
```sh
./main.sh -i /home/user/assembly/slow_fast_degs_hs.fasta -b /home/user/BANCHE_OMOLOGY/diamond -T blastx -t 48 -D -d /home/user/BANCHE_OMOLOGY/NR/nr.dmnd -p 50
```
In this case, we will divide the computation (and the input file) into 50 parts that will be processed simultaneously (with 48 threads each). In the end, the outputs of the 50 jobs will be combined into a single file.

An other example using the BLAST
```sh
./main.sh -i ../project/assembly/slow_fast_degs_hs.fasta -b /home/blast/blastx -T blastx -t 48 -d /home/user/DB/nr -p 100
```

## License

**Free Software, Yeah!**
