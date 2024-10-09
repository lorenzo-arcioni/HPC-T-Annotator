![Build passing](https://img.shields.io/badge/build-passing-success)
![License MIT](https://img.shields.io/badge/license-MIT-success)
![Release Latest](https://img.shields.io/badge/release-latest-blue)

# HPC-T-Annotator
## Introduction

HPC-T-Annotator is a parallelization tool that increases the performance of BLAST and Diamond alignment software. 

The software was developed to be used on large clusters with high performance and not overloaded. If the cluster where it runs is overloaded and the jobs fail to start simultaneously, there will be a considerable degradation in performance.

Visit the  <a href="https://github.com/lorenzo-arcioni/HPC-T-Annotator/wiki">Wiki</a> page for futher informations!

There exists a graphical web interface that semplifies all this boring IT stuff. If you want to use it, please go [here](http://raganella.deb.unitus.it/HPC-T-Annotator/index.html). Else, for command line execution pipeline, read **carefully** instructions below.

## Installation
### Prerequisites

- OS: GNU Linux / Mac (though it's not tested for Mac yet - it _**should**_ work there)
- Python 3.8.15 (or higher)

If you are running on a cluster (where usually several versions are available) make sure to load a given Python 3 version.

### Get started
First, we start by getting the last software release and download it into an empty directory on our filesystem on your local machine (can be also the cluster).
```sh
cd empty_directory
wget https://github.com/lorenzo-arcioni/HPC-T-Annotator/releases/download/v1/hpc-t-annotator.tar.gz
```

And then extract it!

```sh
tar -xvzf hpc-t-annotator.tar.gz && rm hpc-t-annotator.tar.gz
```

The software does not require a further installation process.

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
- `-p <number of processes>`
    Number of processes to split the computation into.
- `-t <threads>`
    The number of threads that each process can use. 

#### BLAST/Diamond further options
It is of course possible to give further options to the BLAST and Diamond software. This is done via prepared files located in the **Bases** directory.
Simply add one-line options in the respective file, depending on which tool you are using BLAST or Diamond.

- `blast_additional_options.txt`
- `diamond_additional_options.txt`

For example, in the diamond additional options file, we can insert:
```sh
--ultra-sensitive --quiet
```
It is **mandatory** to enter the options all on one line.

#### SLURM Execution Configuration

Regarding the execution of HPC-T-Annotator on an HPC cluster with SLURM as the workload manager, the user must ensure to properly configure all the configuration files that reside in the Bases folder, namely:

- `slurm_controlscript_base.txt`
- `slurm_partial_script_base.txt`
- `slurm_start_base.txt`

Remember to properly configure these files, as failure to do so may compromise the entire execution.

Please note that for execution through the SLURM workload manager, it is necessary to provide the **--slurm** option in the command line when running the **main.sh script**.

## Execution pipeline example
Once you have downloaded and extracted the TAR archive, you can proceed as follows: perform the code generation phase, upload (if necessary) the generated TAR package to the HPC machine, and then start the computation. For code generation, GUI is highly recomended!

### Generation of code

#### Interface generation

For GUI code generation, please visit the project [website](http://raganella.deb.unitus.it/HPC-T-Annotator/index.html).

#### Command-line generation
A command-line example using the diamond suite.
```sh
./main.sh -i /home/user/assembly/slow_fast_degs_hs.fasta -b /home/user/BANCHE_OMOLOGY/diamond -T blastx -t 48 -D -d /home/user/BANCHE_OMOLOGY/NR/nr.dmnd -p 50
```
In this case, we will divide the computation (and the input file) into 50 parts that will be processed simultaneously (with 48 threads each). In the end, the outputs of the 50 jobs will be combined into a single file.

An other example using the BLAST
```sh
./main.sh -i /home/user/project/assembly/slow_fast_degs_hs.fasta -b /home/blast/blastx -T blastx -t 48 -d /home/user/DB/nr -p 100
```

In this case we have split the computation into 100 jobs using the BLAST suite.

### Execution on HPC machine
So we extract the generated code (if necessary).
```sh
tar -xf hpc-t-annotator.tar && rm hpc-t-annotator.tar
```
Once this is done, you have everything you need to manage and start the computation, so all you have to do is run (if you are on Slurm):

```sh
sbatch start.sh
```

It is **very important** that *sbatch* command is run in the same directory of .sh file; and **not** "sbatch /some/other/path/start.sh".


Or 

```sh
nohup start.sh 1> start.out 2> start.err &
```

if you are not using a wokload manager.


At the end of the calculation, the output will be in the **tmp** directory with the name **final_blast.tsv**.

## Citation
When using the tool in published research, please cite:

- Arcioni, L., Arcieri, M., Martino, J.D. et al. HPC-T-Annotator: an HPC tool for de novo transcriptome assembly annotation. BMC Bioinformatics 25, 272 (2024). https://doi.org/10.1186/s12859-024-05887-3

## License

Copyright © 2024 Lorenzo Arcioni

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
