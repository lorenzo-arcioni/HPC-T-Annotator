import os
import sys
import datetime

def main():
	
	#Get the tmp dir path
	pwd = os.getcwd() 
	pwd = tmpdir = os.path.join(pwd, "tmp")
	
	stot = 0
	
	max_time = 0
	min_time = 99999999999
	
	#Get a list of all dir in tmp directory
	tmpdir_folders = [ f.name for f in os.scandir(tmpdir) if f.is_dir() ]
	
	#Calculate the max and the min runtime
	for i in tmpdir_folders:
		errfile = os.path.join(tmpdir, i + "/general.err")
		with open(errfile, "r") as file:
			last_line = file.readlines()[-1]
			file.close()
		s = int(float(last_line[:-1]))
		
		stot += s
					
		max_time = max(max_time, s)
		min_time = min(min_time, s)	
	
	#Calculate the average runtime
	smed = stot // len(tmpdir_folders)
	
	#Write all data in the logfile
	print("Average runtime: " + str(datetime.timedelta(seconds=smed)) + "\n")
	print("Max runtime: " + str(datetime.timedelta(seconds=max_time)) + "\n")
	print("Min runtime: " + str(datetime.timedelta(seconds=min_time)) + "\n")
							
				
				
if __name__ == '__main__':
	sys.exit(main())
