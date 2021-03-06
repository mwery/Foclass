#! /usr/bin/env python3
"""
	Used if some input environment are given and we want to remove them from the value
	Take for argument the GINsim result file and make two matrix :
	One with 0* or 1* depending on the mutation (matricemutantStar)
	One with in header name of protein + name of mutations (matricemutantFullTab)
@author : Meline WERY
"""

import glob
import os
import csv
import ast
import sys

def writeMatrixStar(list_prot, dict_state, index, folder):
	""" Write matrix with [0-9]* depending on mutation """

	with open(folder+"/matricemutant.csv", 'w') as csvfile:
		f_out = csv.writer(csvfile, delimiter=',')
		header = [value for pos, value in enumerate(list(list_prot)) if pos not in	 index]
		#header = list(list_prot)
		header.insert(0, "Name")
		f_out.writerow(header)

		i = 0
		for stable_state, mutation_name in dict_state.items():
			i += 1
			for mutant in mutation_name:
				if mutant[:2] == 'WT':
					pheno = mutant+str(i)
					break
				else: # if stable state is only obtain with mutation
					pheno = "SS"+str(i)

			for mutant in mutation_name:
				list_elem = mutant.split(', ')
				list_ss = list(stable_state)
				for elem in list_elem:
					if elem != 'WT':
						indice = header.index(elem[:-3])-1
						if elem[-2:] == 'KO':
							list_ss[indice] = "0*"
						if elem[-2:].startswith('E'):
							list_ss[indice] = elem[-1]+"*"
				list_ss.insert(0, pheno)
				f_out.writerow(list_ss)



def writeMatrixFull(list_prot,list_mutant,  dict_state, dict_input, index, folder):
	""" Write matrix where columns are the protein name + mutation name """

	input_file = open(folder+"/Inputs_SS.tsv", 'w')
	header_input = "Name\tInputs"
	input_file.write(header_input+'\n')

	with open(folder+"/matriceFull.csv", 'w') as csvfile:
		f_out = csv.writer(csvfile, delimiter=',')
		header = [value for pos, value in enumerate(list(list_prot)) if pos not in index]
		header.insert(0, "Name")
		header.extend(list_mutant)
		f_out.writerow(header)
		i = 1

		for stable_state, mutation_name in dict_state.items():
			len_mut = len(list_mutant)
			list_mut = ['0']*len_mut
			for mutant in mutation_name:
				if mutant[:2] == 'WT':
					pheno = mutant+str(i)
					break
				else: pheno = "SS"+str(i)
			list_ss = list(stable_state)
			list_ss.insert(0, pheno)
		   #len_mut=len(list_prot)+1
			for mutant in mutation_name:
				if mutant in header:
					#indice = header.index(mutant)-len(list_prot)-1
					indice = header.index(mutant)-(len(list_prot)-len(index))-1
					list_mut[indice] = "1"
			list_ss.extend(list_mut)
			f_out.writerow(list_ss)
			i += 1

			lst_input = [str(x) for x in dict_input[stable_state]]
			# print(lst_input)
			input_file.write(pheno+'\t'+','.join(lst_input)+'\n')
		input_file.close()

def analysisInput(fileName, folder):
	""" From GINsim result file to dictionnary (stable_state, mutation_name) """

	path = os.path.dirname(fileName)
	fileResult=folder+"/SS_"+str(fileName[:-6])+"txt"
#	fileName=(list(file))[0]
#	fileResult="mutant"+str(fileName[:-6])+"txt"
	#En dehors de Snakemake, file != de <class 'snakemake.io.InputFiles'>

	#print(fileName)
	#fileResult=path+"/mutant"+fileName[:-6]+"txt"
	#path=os.getcwd()
	ginsimotif=path+'scripts/'+"GINsim-*.jar"
	ginsimvers=glob.glob(ginsimotif)
	#print(ginsimvers)
	cmd = "java -cp %s:scripts/extensions/jython-standalone-2.7.0.jar org.ginsim.Launcher -s ./scripts/ginsim/FindStableStateInput.py %s -> %s" %(ginsimvers[0], fileName, fileResult)
	# print(cmd)
	# sys.exit()

	os.system(cmd)
	os.system("sed -i '0,/Jython is available/ d' %s" %(fileResult))

	dict_state = {}
	dict_input = {}
	list_prot = []
	list_mutant = []
	index = []

	with open(fileResult, 'r') as f_in:
		for i, line in enumerate(f_in):
			if i == 0:
				list_prot = line.strip().strip('[]').split(', ')
				#print(len(list_input))
				next_line = f_in.readline()
				list_input = next_line.strip().strip('[]').strip("'").split(', ')
				# print(list_input)
				index = [list_prot.index(inputs) for inputs in list_input if inputs in list_prot]
#				print(len(list_prot))
				next_line = f_in.readline()


				while(next_line):
					current_input = ast.literal_eval(next_line)
					# current_input = next_line.strip().strip('[]').split(', ')
					#print(current_input)
					#current_input = [list_prot[pos] for pos, value in enumerate(curr_input) if list_prot[pos] in curr_input and int(value) == 1]

					next_line = f_in.readline()
					mutant = next_line.strip()

					if mutant not in list_mutant: list_mutant.append(mutant)
					#print(pheno)
					next_line = f_in.readline()

					while(next_line.startswith('0') or next_line.startswith('1')):
						next_line = list(next_line.rstrip('\n'))
					   # print(next_line)
						#print(len(next_line))

						next_line_inputout = [value for pos,value in enumerate(next_line) if pos not in index]


						#print(next_line_inputout)
						#print(len(next_line_inputout))

						next_line_inputout = ''.join(next_line_inputout)

						if next_line_inputout not in dict_state:
							dict_state[next_line_inputout] = []
							dict_state[next_line_inputout].append(mutant)

							dict_input[next_line_inputout]= []
							dict_input[next_line_inputout].append(current_input)
						else:
							value = dict_state[next_line_inputout]
							#print(value)
							if mutant not in value:
								dict_state[next_line_inputout].append(mutant)

							inputs = dict_input[next_line_inputout]
							if current_input not in inputs:
								dict_input[next_line_inputout].append(current_input)

						next_line = f_in.readline()
	#print(dict_state)
		writeMatrixFull(list_prot, list_mutant, dict_state, dict_input, index, folder)
#		writeMatrixStar(list_prot, list_mutant, dict_state, index)

if len(sys.argv) == 3:
	fileGin = sys.argv[1]
	folder = sys.argv[2]+'/'

analysisInput(fileGin, folder)
