def get_multiple_strand_from_fasta(path: str):
	'''
	Takes input from a multifasta file, then for each gene, adds an entry to a dictionary where the key is the gene name and the value is the fasta string.

	Arguments:
		path: str
			The file path

	Returns:
		ret: dict
			The constructed dictionary
	'''
	
	last_header = None

	ret = dict()
	i = 0
	
	lista = path.split("\n")
	
	lista = list(filter(lambda a: a != "", lista))
	
	for line in lista:
		# se inizia con '>' è una nuova sequenza
		if line[0] == '>': 
			# prendo il nome del gene
			last_header = line
			ret[last_header] = "" # inizializzo il suo valore nel dizionario
		# se non inizia con '>' è un pezzo di sequenza
		else:
			ret[last_header] += line # Aggiungo la sequenza all'ultimo gene trovato
	return ret

headers = []

with open("./headers.txt", "r") as f:
    for line in f:
        headers.append(line.strip())

dic = get_multiple_strand_from_fasta(open("../../input/input.fa", 'r').read())

with open("contigs.fa", "w") as f:
    for header in headers:
        f.write(header + "\n")
        f.write(dic[header] + "\n")
    f.close()