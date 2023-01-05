import fasta
import os
import sys
import shutil
import subprocess as sp
from mpi4py import MPI
from datetime import datetime

def main():
	comm = MPI.COMM_WORLD
	size = comm.Get_size()
	rank = comm.Get_rank()

	pwd = os.getcwd() #Ottengo il path corrente
	generallog = os.path.join(pwd, "general.log")
	pwd = tmpdir = os.path.join(pwd, "tmp") #Aggiungo al path il nome della cartella tmp
	logfile = os.path.join(tmpdir, "final.log")

	fasta.init() #inizializzo le opzioni e gli std in e out
	
	format = fasta.outfmt #Ottengo il formato di output dall' opzione
	inputfile = fasta.inputfile
	diamond = int(fasta.diamond) #Parametro che indica l'utilizzo di diamond
	
	dic1 = fasta.get_multiple_strand_from_fasta(sys.stdin.read()) #ottengo il dizionario dal file mfasta con i contigs

	keys = dic1.keys() #Ottengo le chiavi del dizionario (gli headers dei contigs)
	now1 = ""
	n_keys = len(keys) #Ottengo il numero dei contigs
	
	comm.Barrier() #Aspetto che tutti abbiano finito
	
	if rank == 0: # dividing data into chunks
	
	    now1 = datetime.now()
	    
	    chunks   = [[] for _ in range(size)]
	    
	    for i, chunk in enumerate(keys):
	    	chunks[i % size].append(chunk)
	    if os.path.exists(pwd): #Se esiste la cartella tmp la elimino con tutto il suo contenuto
	    	shutil.rmtree("tmp")
	    os.mkdir("tmp")
	    
	    with open(logfile, 'a', encoding='utf-8') as f: #Apro il file di log del lancio
	    	f.write("Sequenze totali: " + str(n_keys) + "\n")
	    	f.write("Processi MPI totali: " + str(size) + "\n")
	    	f.close()	    	
	else:
	    chunks = None

	headers = comm.scatter(chunks, root=0) #Lista delle head dei contigs

	comm.Barrier() #Aspetto che tutti abbiano finito

	#print(str(rank) + ": \n", headers)
	
	pwd = os.path.join(pwd, str(rank))
	os.mkdir(pwd) #Ogni nodo crea una sua cartella per i suoi dati (fasta ed output)
	outfile  = os.path.join(pwd, "blastx.out")
	#errfile  = os.path.join(pwd, str(rank)+ "_blastx.err")
	filename = os.path.join(pwd, "contigs.fa")
	script   = os.path.join(pwd, "script.sh")
	
	with open(filename, 'w', encoding='utf-8') as f: #ogni nodo genera un suo file fasta contenente le sequenze
		for h in headers:
			f.write(">" + h + '\n')
			f.write(dic1[h] + '\n')
		f.close()
		
	with open(script, 'w', encoding='utf-8') as f:   #Ogni nodo genera un suo script sbatch
		f.write("#!/bin/sh\n"+
		        "#SBATCH --job-name=Proc-" + str(rank) + "\n" +
		        "#SBATCH --output=tmp/" + str(rank) + "/general.out\n"+
		        "#SBATCH --error=tmp/" + str(rank) + "/general.err\n"+
		        "#SBATCH --mem=6GB\n"+
		        "#SBATCH --time=10:00:00\n"+
		        "#SBATCH --nodes=1\n"
		        "#SBATCH --ntasks-per-node=12\n"+
		        "#SBATCH --account=Paolo\n"+
		        "#SBATCH -p partition_paolo\n")
		#f.write("module load autoload profile/bioinf\nmodule load autoload blast+/2.12.0\n")
		bin_path = "binary_paolo"
		db_path  = "db_paolo"
		if diamond:
			f.write("/usr/bin/time -f \"%e\"" + str(bin_path) + " blastx -q " + filename + 
				                              " -d " + str(db_path) + " -o " + outfile + 
				                              " -p $SLURM_NTASKS_PER_NODE -f " + format[1:-1] + "\n") 
		else:
			f.write("/usr/bin/time -f \"%e\"" + str(bin_path) + " -query " + filename + 
				                              " -db " + str(db_path) + " -out " + outfile +
				                              " -num_threads $SLURM_NTASKS_PER_NODE -outfmt " + format + "\n")
		f.close()
		
	sp.call("chmod 777 ./tmp/" + str(rank) + "/" + "script.sh", shell=True)	#Rendo eseguibile lo script
	sp.call("sbatch -W ./tmp/" + str(rank) + "/" "script.sh", shell=True)    #Lancio lo script
	
	comm.Barrier() #Aspetto che tutti abbiano finito
	
	if rank == 0:
		final_outfile = os.path.join(tmpdir, "final_blastx.tsv")
		
		with open(final_outfile, 'w', encoding='utf-8') as f: #Creo il file finale degli output
			for i in range(size):
				pwd = os.path.join(tmpdir, str(i))
				with open(os.path.join(pwd, "blastx.out"), 'r', encoding='utf-8') as t:
					f.write(t.read())
					t.close()
			f.close()
		sp.call("python3 time_calculator.py", shell=True)	#Eseguo lo script che calcola i tempi
		now2 = datetime.now()
		with open(generallog, 'a', encoding='utf-8') as f: #Apro il file finale di log
			f.write(str(now1) + "\n")
			f.write("Input file: " + inputfile + "\n")
			f.write("out-format: " + format + "\n")
			f.write(open("./tmp/final.log", 'r', encoding='utf-8').read())
			f.write("Utilizzo Diamond: " + ("si" if diamond else "no") + "\n")
			f.write(str(now2) + "\n")
			f.write("-------------------------------------------------\n")
			f.close()	    	
	
if __name__ == '__main__':
    sys.exit(main())