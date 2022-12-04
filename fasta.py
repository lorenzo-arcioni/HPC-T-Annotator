import sys

from optparse import OptionParser

outfmt    = "\"6 qseqid sseqid slen qstart qend length mismatch gapopen gaps sseq\""
inputfile = ""
diamond   = 0

def init():
	global outfmt
	global inputfile
	global diamond
	
	#Defining the options
	parser = OptionParser()
	parser.add_option("-o", "--output", dest="filename_o",
		          help="output file name", metavar="FILE")
	parser.add_option("-f", "--outformat", dest="filename_outfmt",
		          help="output file format", metavar="FILE")
	parser.add_option("-i", "--input", dest="filename_i",
		          help="input file name", metavar="FILE")
	parser.add_option("-d", "--diamond", dest="filename_d",
		          help="using diamond", metavar="FILE")

	(options, args) = parser.parse_args()

	#Takes the arguments from the command-line
	if options.filename_o != None:
		sys.stdout = open(options.filename_o, 'w') 
	if options.filename_i != None:
		sys.stdin = open(options.filename_i, 'r')
		inputfile = options.filename_i
	if options.filename_outfmt != None:
		outfmt = options.filename_outfmt
	if options.filename_d != None:
		diamond = options.filename_d
	

def get_multiple_strand_from_fasta(path: str):
	'''
	Takes in input the multifasta file, and after that takes each gene and add to a dict
	the entry that has as key the name of the gene and as value the fasta string.
	Arguments:
	    path: str
		the file path
	Returns:
	    ret: dict
		The dictionary obtained
	'''
	
	last_header = None

	ret = dict()
	i = 0
	
	lista = path.split("\n")
	
	lista = list(filter(lambda a: a != "", lista))
	
	for line in lista:
		# if the string start with '>' it's a new sequence
		if line[0] == '>': 
			last_header = line[1:]
			ret[last_header] = "" 
		# if the string don't start with '>' it's a slice of a sequence
		else:
			ret[last_header] += line.strip().upper()
	return ret 

def find_orf(sequence: str):
	lst = []
	
	begin = 0
	while True:
		
		begin = sequence.find("ATG")
		
		if begin < 0:
			break
		
		for i in range(begin, len(sequence)-2):
			if sequence[i:i+3] in ["TAG", "TAA", "TGA"] and i - begin > 100:
				lst.append((begin, i+3))
		sequence = sequence[:begin] + "F" + sequence[begin+1:]
		
		begin += 3
	return lst
	
def conta(codice: str, verbose: bool = True):
	'''
	Given a fasta sequence, returns a dict with 5 entries (one per base) and a counter for each of them.
	Argunments:
	    fasta string: str
	    verbose: bool
		if we want more details
	Returns:
	    the built dict.
	'''
	# inizializzo il dizionario
	name_mapping = {'A': 'Adenina', 'C': 'Citosina', 'G': 'Guanina', 'T': 'Timina', 'U': 'Uracile'}
	ret = dict()
	# per ogni carattere
	for c in codice:
		c = c.upper()
		if c not in ['A', 'T', 'C', 'G', 'U']: #qualcosa non va
			continue
		else:
			if c in ret: # semplicemente aggiungo 1 alla base corrispondente
				ret[c] += 1
			else:
				ret[c] = 1
	if verbose: # faccio dei print più descrittivi
		for k in ret:
			if ret[k] == 0 and k in ['U', 'T']:
				continue
			print(f"Nucleobases: {name_mapping[k]}({k}) count: {ret[k]} frequency: {round(ret[k]*1.0/sum(ret.values())*100, 3)}")

	return ret

def offsetize(seq: str, offset: int = 69): # Format the sequence with given offset
	i = 0
	lst = []
	while True:
		if len(seq[i:]) > offset:
			lst.append(seq[i : i + offset + 1])
			i = i + offset + 1
		else:
			if seq[i:] != '':
				lst.append(seq[i:])
			break
	return lst
			
def store_fasta(dic: dict, offset: int = 69): #Print the dict with sequences on stdout
	for k in dic.keys():
		print(">" + k)
		
		for x in offsetize(dic[k], offset):
			print(x)

def store_orf(fasta_dic: dict): #Print the dict with found orf on stduot

	orf = dict()
	
	for x in fasta_dic.keys():
		tup = find_orf(fasta_dic[x])
		i = 1
		for k in tup:
			print(">" + x + " orf " + str(i))
			for y in offsetize(fasta_dic[x][k[0]:k[1]]):
				print(y)
			i += 1

# Translate the codons to proteins
def translate(seq: str):
      
    table = {
        'ATA':'I', 'ATC':'I', 'ATT':'I', 'ATG':'M',
        'ACA':'T', 'ACC':'T', 'ACG':'T', 'ACT':'T',
        'AAC':'N', 'AAT':'N', 'AAA':'K', 'AAG':'K',
        'AGC':'S', 'AGT':'S', 'AGA':'R', 'AGG':'R',                
        'CTA':'L', 'CTC':'L', 'CTG':'L', 'CTT':'L',
        'CCA':'P', 'CCC':'P', 'CCG':'P', 'CCT':'P',
        'CAC':'H', 'CAT':'H', 'CAA':'Q', 'CAG':'Q',
        'CGA':'R', 'CGC':'R', 'CGG':'R', 'CGT':'R',
        'GTA':'V', 'GTC':'V', 'GTG':'V', 'GTT':'V',
        'GCA':'A', 'GCC':'A', 'GCG':'A', 'GCT':'A',
        'GAC':'D', 'GAT':'D', 'GAA':'E', 'GAG':'E',
        'GGA':'G', 'GGC':'G', 'GGG':'G', 'GGT':'G',
        'TCA':'S', 'TCC':'S', 'TCG':'S', 'TCT':'S',
        'TTC':'F', 'TTT':'F', 'TTA':'L', 'TTG':'L',
        'TAC':'Y', 'TAT':'Y', 'TAA':'_', 'TAG':'_',
        'TGC':'C', 'TGT':'C', 'TGA':'_', 'TGG':'W',
    }
    
    protein = ""
    
    seq = seq.replace("\n", "")
    seq = seq.replace("\r", "")
    
    if len(seq)%3 == 0:
        for i in range(0, len(seq), 3):
            codon = seq[i:i + 3]
            protein += table[codon]
    	
    return protein
