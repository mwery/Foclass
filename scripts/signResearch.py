#! /usr/bin/env python3
# -*- coding: utf-8 -*-

""" Find the signature of a phenotype depending on the type of data (expressed protein, pre-classification of some stable states or GINsim result file)


@author : Meline WERY
"""

import os
import csv
import re

from glob import glob

import concepts
from concepts import Context
#from matrixFCA import readMatrixFCA
#from parcoursGraph import *


def are_eq(list1, list2):
    """ Check if two list contain all the same element """

    return set(list1) == set(list2) and len(list1) == len(list2)


def dataMatrix(filepath):
    """Construction of the complete matrix"""

    dict_object = {}
    with open(filepath, "rt") as matrix_file:
        readertext = csv.reader(matrix_file, delimiter=',')
        header = readertext.__next__()
        #print("HEADER:")
        #print(header)
        list_column_header = header[1:]
        number_columns = len(list_column_header)
        #for currentColHeader in list_column_header:
            #print("  " + currentColHeader)
        #print("  => " + str(number_columns) + " columns")
        #print("")
        for current_row in readertext:
            #print("")
            #print(current_row)
            current_object = current_row[0]
            dict_object[current_object] = []
            for i in range(number_columns):
                if current_row[i+1] == '1':
                    #print("  " + list_column_header[i])
                    dict_object[current_object].append(list_column_header[i])

    definition = concepts.Definition()
    for (current_object, current_values) in dict_object.items():
        definition.add_object(current_object, current_values)
    context = concepts.Context(*definition)
    return context


def analysisBySign(file_signature):
    """ Fonction to research type by given signature """

    dict_signature = {}
    #file_signature = input("Signature file : ")
    with open(file_signature, 'r') as sign_file:
        for line in sign_file:
            if line.startswith('#By signature'):
                next_line = sign_file.readline()
                while not next_line.startswith('#By phenotype'):
                    signature_name = next_line.split('=')[0]
                    list_signature = next_line.strip().split('=')[1]
                    list_signature = list_signature.split(',')

                    dict_signature[signature_name] = list_signature
                    next_line = sign_file.readline()

    return dict_signature


def analysisByPheno(context):
    """ Fonction to research type by given some phenotype """

    list_pheno = []
    dict_pheno = {}
    with open('signature.txt', 'r') as pheno_file:
        for line in pheno_file:
            if line.startswith('#By phenotype'):
                next_line = pheno_file.readline()
                while next_line:
                    phenotype_name = re.sub(r'(\w*)=(.+)', r'\1', next_line).strip()
                    if not phenotype_name == '': dict_pheno[phenotype_name] = []
                    else: break
                    list_pheno = re.sub(r'(\w*)=(.+)', r'\2', next_line).strip()
                    list_pheno = list_pheno.split(',')
                    list_protein = context.intension(list_pheno)
                    dict_pheno[phenotype_name] = (list(list_protein))
                    next_line = pheno_file.readline()

    return dict_pheno


def analysisByGINsimFile(path):
    """Fonction to research type by GINsim results in WT"""

    file = glob(path+'/*.txt')[0]
    dict_wt = {}
    with open(file, 'r') as f_in:
        for i, line in enumerate(f_in):
            if i == 0:
                list_protein = line.strip().strip('[]').split(', ')
                pheno = f_in.readline().strip()                     #Comment on reduction or not
#                for elem in listProt:
#                    if elem=="IL12":
#                        indexIL12=listProt.index(elem)
#                listProtOut12=listProt[:indexIL12]+listProt[indexIL12+1:]
                #print(indexIL12)
                #print (listProt)
                next_line = f_in.readline()              #Start of stable states

                list_pheno = []
                n = 1
                while next_line.startswith("0") or next_line.startswith("1"):
                    #print(len(next_line))
                    next_line = next_line.rstrip('\n')

#                    next_lineIL12out=next_line[:indexIL12]+next_line[indexIL12+1:]
                    set_protein = []
                    i = 0

                    for val in next_line:
                        if val == '1':
                            set_protein.append(list_protein[i])
                        i += 1
                    if set_protein not in list_pheno:
                        list_pheno.append(set_protein)
                        dict_wt[pheno+str(n)] = set_protein
                        n += 1
                    next_line = f_in.readline()

    return dict_wt

def researchSignature(fileCSV, sign):
    """ Main fonction of the module """

    path = os.path.dirname(fileCSV)
#    print(filepath)
    context = dataMatrix(fileCSV)
    #print(context)

    #print("Research by signature (s), phenotype (p) or by GINsim results file (g) (quit q)?")
    #rep = input()

    #while rep not in ['s', 'p', 'q', 'g']:
    #    print("Sorry. This answer is not known. s/p ?")
    #    rep = input()

    #if rep == 's':
    dict_wt = analysisBySign(sign)
    #elif rep == 'p':
    #    dict_wt = analysisByPheno(context)
    #elif rep == 'g':
    #    dict_wt = analysisByGINsimFile(path)
    #elif rep == 'q':
    #    exit(1)
    #print(dict_wt)
    return dict_wt

#main()

