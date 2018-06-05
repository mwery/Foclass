#! /usr/bin/env python3
""" Determine the sub-concept of a set of attribute concepts
    Find if a steady stable state is in the set of objects of this sub-concept

@author : Meline WERY
 """

import csv, re, os, sys, time

import concepts
from concepts import Context
from pandas import DataFrame
#from parcoursGraph import *
#from colorGraph import
#import parcoursGraph as PG
import signResearch as RS

#from reportlab.pdfgen import canvas
#from reportlab.lib.units import cm

#from matplotlib import pyplot as plt
#import numpy as np
#from scipy.spatial.distance import pdist
#from scipy.cluster.hierarchy import linkage, dendrogram
#from mpl_toolkits.axes_grid1 import make_axes_locatable

#import time
#import progressbar

file_csv = sys.argv[1]
file_result = sys.argv[2]
file_sign = sys.argv[3]
path = os.path.dirname(file_csv)
#print("file open")
#print("start prog")


def readMatrixFCA(file_csv):
    """ FCA matrix to dict """

    dict_objects = {}
    if file_csv.endswith(".csv"):
        delimiter = ","
    elif file_csv.endswith(".tsv"):
        delimiter = "\t"
    else:
        delimiter = "\t"

    with open(file_csv, "rt") as matrixFile:
        readertext = csv.reader(matrixFile, delimiter=delimiter)
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
            dict_objects[current_object] = []
            for i in range(number_columns):
                if current_row[i+1] == '1' or current_row[i+1] == '2':
#                    print("  " + list_column_header[i])
                    dict_objects[current_object].append(list_column_header[i])
    return dict_objects


def readMatrix(file_result):
    """ From matricemutantWTKOE1 file to a dictionnary (phenotype_name, mutation_name) """

    dict_state = {}
    with open(file_result, 'r') as f_in:
        readertext = csv.reader(f_in, delimiter=',')
        header = readertext.__next__()
        list_column_header = header[1:]
        number_columns = len(list_column_header)
        for current_row in readertext:
            current_stablestate = current_row[0]
            dict_state[current_stablestate] = []
            for i in range(number_columns):
                if current_row[i+1] == '1':
                    if list_column_header[i] == 'WT':
                        dict_state[current_stablestate].append(list_column_header[i])
                        break
                    else: dict_state[current_stablestate].append(list_column_header[i])

    return dict_state

def dictToConcept(data_matrix):
    """ From dictionnary to concepts """

    definition = concepts.Definition()
    for (current_obj, current_values) in data_matrix.items():
        definition.add_object(current_obj, current_values)
    context = Context(*definition)
    lattice = context.lattice

    return context, lattice


def patternMotifempty(concept, stablestate):
    """ If attribute of phenotype's formal concept is empty """

    if re.match(r'{(.+)}\s<->\s(\[(.+)?\])\s<=>\s(.+)',concept):
        objects = re.sub(r'{(.+)}\s<->\s(\[(.+)?\])\s<=>\s(.+)', r'\4', concept)
        nobjects = re.sub(r'(\w)(\s<=>(.+))?', r'\1', objects)
    else:
        return False
    return stablestate == nobjects

def patternMotif(concept, stablestate):
    """ If attribute of phenotype's formal concept is not empty """

    objects = re.sub(r'{(.+)} <-> \[(.+)\]( <=> (.+))?', r'\1', concept)
    listobjects = objects.split(', ')
    return stablestate in listobjects

def writeFinalFile(path, dict_assoc, list_wt, ens_obj):
    """ Write on a file the signature with associated stable states """

    dict_wt = {}
    list_pheno = []
    f_out = open(path+'/AssociationPheno.txt', 'w')
    for protein, stable_state in dict_assoc.items():
        for sign in list_wt:
            if tuple(sign[1]) == protein:
                name = sign[0]
        f_out.write('La signature de '+name+' : '+str(protein)+'\n')
        pheno = [sign[1] for sign in list_wt if tuple(sign[1]) == protein]
        dict_wt[str(pheno[0])] = stable_state
        f_out.write('Les etats stables associes : '+str(stable_state)+'\n')
        f_out.write('')
        list_pheno.extend(stable_state)


    f_out.write('\n')
    list_rest = [elem for elem in ens_obj if elem not in list_pheno]
    f_out.write('Les etats qui ne sont pas associes : '+str(list_rest)+'\n')
    f_out.close()

    return list_rest, dict_wt


def createpdf(filepath):
    pdf = canvas.Canvas(filepath[:-4]+'.pdf')
    pdf.drawString(3*cm, 25*cm, u'Representative graph of '+os.path.basename(filepath)[:-4])
    pdf.line(3*cm,24.5*cm,18*cm,24.5*cm)
    pdf.drawString(3*cm, 23*cm, u'Sorry, this graph is too big...')
    pdf.save()
    return

def drawheatmap(data, title, path):
    main_axes = plt.gca()
    divider = make_axes_locatable(main_axes)

    plt.sca(divider.append_axes("left", 1.0, pad=0))
    ylinkage = linkage(pdist(data, metric='euclidean'), method='average', metric='euclidean')
    ydendro = dendrogram(ylinkage, orientation='left', no_labels=True, distance_sort='descending', link_color_func=lambda x: 'black')
    plt.gca().set_axis_off()
    data = data.ix[[data.index[i] for i in ydendro['leaves']]]

    plt.sca(main_axes)
    plt.imshow(data, aspect='auto', interpolation='none', cmap=plt.cm.Blues)
    plt.colorbar(pad=0.15)
    plt.gca().yaxis.tick_right()
    plt.yticks(range(data.shape[0]), data.index, size='small')
    plt.xticks(range(data.shape[1]), data.columns, size='small')
    plt.gca().xaxis.set_ticks_position('none')
    plt.gca().yaxis.set_ticks_position('none')
    plt.gca().invert_yaxis()


    #plt.show()
    plt.savefig(title+'.pdf')
    plt.clf()

def heatmap(list_rest, list_wt, data_matrix, path):
    list_pheno = []
    dico_difference = {}
    dico_commun = {}
    for couple in list_wt:
        pheno_name = couple[0]
        list_pheno.append(pheno_name)
        signature = couple[1]
        for reste in list_rest:
            for SS_name, SS_prot in data_matrix.items():
                if reste == SS_name:
                    difference = set(SS_prot).symmetric_difference(set(signature))
                    distance = len(difference)
                    commun = set(SS_prot).intersection(set(signature))
                    try:
                        pourcentage = (len(commun)/len(signature))*100
                    except ZeroDivisionError:
                        pourcentage = 0

                    if SS_name not in dico_commun:
                        dico_commun[SS_name] = []
                        dico_commun[SS_name].append(pourcentage)
                    else:
                        dico_commun[SS_name].append(pourcentage)

                    if SS_name not in dico_difference:
                        dico_difference[SS_name] = []
                        dico_difference[SS_name].append(distance)
                    else:
                        dico_difference[SS_name].append(distance)
    list_commun = []
    list_distance = []
    list_SS = []
    for cle1, valeur1 in dico_commun.items():
        for cle2, valeur2 in dico_difference.items():
            if cle1 == cle2:
                list_commun.append(valeur1)
                list_distance.append(valeur2)
                list_SS.append(cle1)

    commun = DataFrame(list_commun, index=list_SS, columns=list_pheno)
    drawheatmap(commun, "Pourcentage de marqueurs en commun", path)
    diff = DataFrame(list_distance, index=list_SS, columns=list_pheno)
    drawheatmap(diff, "Distance = distance entre les protéines exprimées", path)

def analysisByBorne(file_csv, file_result, file_sign, path):
    """ Association of steady stable states with phenotype describing by the WT """
    start = time.time()
    #print("start")

    list_wt = []
    dico_wt = RS.researchSignature(file_csv, file_sign)
    for name, sign in dico_wt.items():
        list_wt.append((name, sign))

    dict_assoc = {}
    list_concept_mutation = []
    list_marqueur = [tuple(sign[1]) for sign in list_wt]
    #print(list_marqueur)

    data_matrix = readMatrixFCA(file_csv)
    context, lattice = dictToConcept(data_matrix)
    bottom = lattice.infimum
    #print("lattice created")


    for pheno in list_wt:
        dict_assoc[tuple(pheno[1])] = []
        list_concept_mutation.append((pheno[1],[]))


    dict_mutant = readMatrix(file_result)
    for stablestate_name, mutation_name in dict_mutant.items():
        if len(mutation_name) > 1:                                          # if there is several mutation for one stable state
            mutation_name = [mutation_name[0]]
        mutation = mutation_name[0].split(', ')

    # If one of the signature has no protein then, for WT, if the stable state is in neither the signature with proteins, it is associated with the empty one.
        empty_FC = stablestate_name

    # Form of formal_concept : [Prot1, Prot2 ...] --> This the list of proteins in each signature

        for formal_concept in list_marqueur:
            if formal_concept != ('empty',):
                list_join = []
                list_indice = []
                for elem in mutation:
                    if elem[-2:] == 'E1' and elem[:-3] not in list(formal_concept):
                        list_join.append(lattice[elem[:-3],])
                    if elem[-2:] == 'KO' and elem[:-3] in list(formal_concept):
                        indice = formal_concept.index(elem[:-3])
                        list_indice.append(indice)
                for prot in formal_concept:
                    if formal_concept.index(prot) not in list_indice:
                        list_join.append(lattice[prot,])

                sub_concept = str(lattice.meet(list_join))
                if sub_concept != str(bottom) and patternMotif(sub_concept, stablestate_name):
                   dict_assoc[formal_concept].append(stablestate_name)
                   empty_FC = ''
                   for elem in list_concept_mutation:
                       if elem[0] == list(formal_concept):
                           elem[1].append(mutation_name)


            else:    # if attribute of formal concept is empty
                list_join = []
                for elem in mutation:
                    if elem[-2:] == 'WT' and empty_FC != '':
                        dict_assoc[formal_concept].append(stablestate_name)

                    if elem[-2:] == 'E1':
                        list_join.append(lattice[elem[:-3],])
                sub_concept = str(lattice.meet(list_join))
                if patternMotifempty(sub_concept, stablestate_name):
                    dict_assoc[formal_concept].append(stablestate_name)
                    for elem in list_concept_mutation:
                        if elem[0] == list(formal_concept):
                            elem[1].append(mutation_name)

    ens_objet = list(context.objects)
    list_rest, dico_wt = writeFinalFile(path, dict_assoc, list_wt, ens_objet)
    #print("Time (sec) : "+str(time.time()-start))

analysisByBorne(file_csv, file_result, file_sign, path)

#    print(path+'/DicoForHisto.txt')
#    # print(list_concept_mutation)
#    with open(path+'/DicoForHisto.txt','a') as dicofile:
#        dicofile.write('#DicoBorne\n')
#        for signat, ens_SS in dico_wt.items():
#            dicofile.write(signat+'='+str(ens_SS)+'\n')

#    with open(path+'AssociationSignMutation.txt', 'w') as f_in:
#        for elem in list_concept_mutation:
#            f_in.write('La signature est : '+str(elem[0])+'\n')
#            f_in.write('L\'ensemble des mutations associées est : '+str(elem[1])+'\n')
#    color_Graph(path+"/matricemutantProtTab.dot", dict_wt)

#    heatmap(list_rest, list_wt, data_matrix, path)
#
#    d = concepts.Definition()
#    for (current_object, currentValues) in data_matrix.items():
#        if current_object in list_rest :
#            d.add_object(current_object, currentValues)
##    for name, sign in dico_wt.items():
##        d.add_object(name, sign)
#    c = concepts.Context(*d)
#    l=c.lattice
#    graphe = l.graphviz()
#    with open(path+"/matricemutantRest.dot", "w") as dotFile:
#        dotFile.write(graphe.source)
#
#    if os.path.getsize(path+'/matricemutantRest.dot') > 50000 :
#        createpdf(path+'/matricemutantRest.dot')
#    else :
#        graphe.render(filename=path+"/matricemutantRest", cleanup=True)
#    #PG.parcours_Graph(path+"/matricemutantRest.dot")
