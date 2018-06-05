#! /usr/bin/env python3
""" 
    Used if some input environment are given and we want to keep it into the value
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

if len(sys.argv) == 3:
    fileResult = sys.argv[1]
    folder = sys.argv[2]+'/'

def writeMatrixStar(list_prot, dict_state, folder):
    """ Write matrix with 0* or 1* depending on mutation """
    with open(folder+"matricemutantStar.csv", 'w') as csvfile:
        f_out = csv.writer(csvfile, delimiter=',')
        header = list(list_prot)
        header.insert(0, "Name")
        f_out.writerow(header)
        i = 0
        for stable_state, mutation_name in dict_state.items():
            i += 1
            for elem in mutation_name:
                if elem[:2] == 'WT':
                    pheno = elem+str(i)
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
                        if elem[-2:] == 'E1':
                            list_ss[indice] = "1*"
                list_ss.insert(0, pheno)
                f_out.writerow(list_ss)
def writeMatrixFull(list_prot, list_mutant, dict_state, folder):
    """ Write matrix where columns are the protein name + mutation name """
#    with open('DicoForHisto.txt', 'w') as dicofile:
#        dicofile.write('#DicoFull\n')
#        dicofile.write(str(list_mutant)+'\n')
    with open(folder+"matricemutantFullTab.csv", 'w') as csvfile:
        f_out = csv.writer(csvfile, delimiter=',')
        header = list(list_prot)
##               header.remove('IL12')
        header.insert(0, "Name")
#               print(list_mutant)
        header.extend(list_mutant)
#               listeKO=[str(elem)+" KO" for elem in list_prot]
#               header.extend(listeKO)
#               listeE1=[str(elem)+" E1" for elem in list_prot]
#               header.extend(listeE1)
        f_out.writerow(header)
        i = 1

        for stable_state, mutation_name in dict_state.items():
            len_mut = len(list_mutant)
            list_mut = ['0']*len_mut
#                   if key=="00000000000" : pheno="Th0"
#                   elif key=="10000000101": pheno="Th1"
#                   elif key=="10001001101": pheno="Th1*"
#                   elif key=="01010010010": pheno="Th2"
            for mutant in mutation_name:
                if mutant[:2] == 'WT':
                    pheno = mutant+str(i)
                    break
                else: pheno = "SS"+str(i)
#                dicofile.write(pheno+'='+str(mutation_name)+'\n')
            list_ss = list(stable_state)
            list_ss.insert(0, pheno)
           #len_mut=len(list_prot)+1
           #print (list_mut)
            for mutant in mutation_name:
                if mutant in header:
                    indice = header.index(mutant)-len(list_prot)-1
                    list_mut[indice] = "1"
            list_ss.extend(list_mut)
            f_out.writerow(list_ss)
            i += 1
def readGINsimNetworkMutant(fileName, folder):
    """ From GINsim result file to dictionnary (stable_state, mutation_name) """
    path = os.path.dirname(fileName)
    fileResult=folder+"/mutant"+str(fileName[:-6])+"txt"
    #En dehors de Snakemake, file != de <class 'snakemake.io.InputFiles'>
    #fileResult="mutant"+filename[:-6]+"txt"
    #path=os.getcwd()
    ginsimotif=path+'scripts/'+"GINsim-*.jar"
    #print(ginsimotif)
    ginsimvers=glob.glob(ginsimotif)
    #print(ginsimvers)
    os.system("java -jar %s -s ./scripts/ginsim/FindStableStateInput.py %s > %s" %(ginsimvers[0], fileName, fileResult))
    list_mutant = []
    dict_state = {}
    list_prot = []
    with open(fileResult, 'r') as f_in:
        for i, line in enumerate(f_in):
            if i == 0:
                list_prot = line.strip().strip('[]').split(', ')
                pheno = f_in.readline().strip()                     #Commentaire sur reduction ou non
                next_line = f_in.readline()              #Debut des etats stables

                while next_line.startswith("0") or next_line.startswith("1"):
                    next_line = next_line.rstrip('\n')
                    if next_line not in dict_state:
                        dict_state[next_line] = []
                        dict_state[next_line].append(pheno)
                    else: dict_state[next_line].append(pheno)
                    next_line = f_in.readline()
                if pheno not in list_mutant:
                    list_mutant.append(pheno)
            else:
                pheno = next_line.rstrip('\n')  #Type de mutant
                next_line = f_in.readline() #Debut des etats stables
                if pheno not in list_mutant:
                    list_mutant.append(pheno)
                while next_line.startswith("0") or next_line.startswith("1"):
                    if len(next_line) > len(list_prot)+1:
                        next_line = next_line.rstrip('\n').split(' ')[0]
                    else:
                        next_line = next_line.rstrip('\n')
                    if next_line not in dict_state:
                        dict_state[next_line] = []
                        dict_state[next_line].append(pheno)
                    else: dict_state[next_line].append(pheno)
                    next_line = f_in.readline()
    #writeMatrixStar(list_prot, dict_state, folder)
    writeMatrixFull(list_prot, list_mutant, dict_state, folder)

    
#                        next_lineIL12out=next_line[:indexIL12]+next_line[indexIL12+1:]
#                    for elem in list_prot:
#                        if elem=="IL12":
#                            indexIL12=list_prot.index(elem)
                #print(indexIL12)
                #print (list_prot)
#                        next_lineIL12out=next_line[:indexIL12]+next_line[indexIL12+1:]
##                    elif key=="10000000101" : pheno="Th1"
##                    elif key=="10001001101" : pheno="Th1*"
##                    elif key=="01010010010" : pheno="Th2"
#fileResult = 'mutantThBooleankoe1.txt'
readGINsimNetworkMutant(fileResult, folder)
