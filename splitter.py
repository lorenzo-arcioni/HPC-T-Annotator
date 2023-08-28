def get_multiple_strand_from_fasta(path: str):
	'''
	Prende in input il file multifasta, dopo di chè per ogni gene aggiunge in un dizionario
	l'entry che ha per chiave il nome del gene e per valore la stringa fasta
	Arguments:
	    path: str
		il path del file
	Returns:
	    ret: dict
		il dizionario costruito
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