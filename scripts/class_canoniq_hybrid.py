#!/usr/bin/env python3

"""
Determine the sub-concept of a set of attribute concepts
Find if a steady stable state is in the set of objects of this sub-concept
Class each fixed point in canonical class and then identify hybrid classes.


@author : Meline WERY
@date  : 5/02/2018
@mail : meline.wery@irisa.fr"""

import csv, re, os, sys, time

import concepts
from concepts import Context
from concepts import lattices

import pandas as pd
#from parcoursGraph import *
#from colorGraph import
#import parcoursGraph as PG
import signResearch as RS

import graphviz

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

#file_csv = 'matricemutantProtTab.csv'
#file_result = 'matricemutantWTKOE1Tab.csv'

def extractHybrid2(dict_hybrid, list_fixpoint, list_signature, dico):
    """ Extract fixed points that are present in one canonical class and one hybrid ==> create new class : hybrid """

    new_dict = dict_hybrid.copy()
    #print(new_dict)
    #hybrid_read = set(frozenset(i) for i in lst_hybrid_read)


    for hybrid_sign, current_hybrid in dict_hybrid.items():
        for j, s in enumerate(list_fixpoint):
            if list_signature[j] not in ["empty", "neither"] and not set(list_signature[j].split(',')).issubset(set(hybrid_sign.split(','))) :
                hybrid_read = [set(x.split(',')) for x in list(new_dict)]
                new_hybrid = [x for x in current_hybrid if x in s]
                old_sign = set(hybrid_sign.split(','))
                new_hybrid_signature = hybrid_sign+','+list_signature[j]
                #print(new_hybrid_signature)
                #print(new_hybrid)
                if new_hybrid != []:
                    # To maintain the overlap, comment the 4 next lines
                    #print(new_hybrid_signature)
                    #print(new_hybrid)
                    curr_hybrid = [x for x in dict_hybrid[hybrid_sign] if x not in new_hybrid]
                    new_dict[hybrid_sign] =  curr_hybrid

                    new_canon = [x for x in dico[list_signature[j]] if x not in new_hybrid]
                    dico[list_signature[j]] =  new_canon

                    if set(new_hybrid_signature.split(',')) not in hybrid_read :
                        new_dict[new_hybrid_signature] = new_hybrid

    if len(new_dict) > len(dict_hybrid) :

        new_dict, dico = extractHybrid2(new_dict, list_fixpoint, list_signature, dico)

    return new_dict, dico


def extractHybride(dico):
    """ Extract fixed points that are present in several canonical classes ==> create new class : hybrid """

    list_signature = []
    list_fixpoint = []
    hybrid_read = []
    dict_hybrid = {}

    for signature, fixpoint in dico.items() : # {proteins of signature : [classified fixed points]}
        list_signature.append(signature)
        list_fixpoint.append(fixpoint)

    # Create the first hybrid (between two canonical classes)

    for i, current_list in enumerate(list_fixpoint) :
        if list_signature[i] not in ["empty", "neither"] :
            for j, test_lst in enumerate(list_fixpoint):
                if i != j and list_signature[j] not in ["empty", "neither"] :
                    hybrid = [x for x in current_list if x in test_lst]
                    hybrid_signature = list_signature[i]+','+list_signature[j]

                    if set(hybrid_signature.split(',')) not in hybrid_read and hybrid != []:
                        dict_hybrid[hybrid_signature] = hybrid
                        hybrid_read.append(set(hybrid_signature.split(',')))

                        # To maintain the overlap, comment the 4 next lines
                        current_lst = [x for x in dico[list_signature[i]] if x not in hybrid]
                        dico[list_signature[i]] =  current_lst

                        tst_lst = [x for x in dico[list_signature[j]] if x not in hybrid]
                        dico[list_signature[j]] =  tst_lst
    #print(dict_hybrid)
    all_hybrid, dico = extractHybrid2(dict_hybrid, list_fixpoint, list_signature, dico)
    #print(all_hybrid)
    dico_final ={**dico, **all_hybrid}

    # If hybrid identification leaves some class empty
    dico_final = {i:dico_final[i] for i in dico_final if dico_final[i]!=[]}
    #print("dico_final")
    #print(dico_final)

    return dico_final



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
                if int(current_row[i+1]) >= 1 :
                    #print("  " + list_column_header[i])
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
    #lattice = context.lattice


    return context


def patternMotifempty(concept, stablestate):
    """ If attribute of phenotype formal concept is empty """

    if re.match(r'{(.+)}\s<->\s(\[(.+)?\])\s<=>\s(.+)',concept):
        objects = re.sub(r'{(.+)}\s<->\s(\[(.+)?\])\s<=>\s(.+)', r'\4', concept)
        nobjects = re.sub(r'(\w)(\s<=>(.+))?', r'\1', objects)
    else:
        return False
    return stablestate == nobjects

def patternMotif(concept, stablestate):
    """ If attribute of phenotype formal concept is not empty """

    objects = re.sub(r'{(.+)} <-> \[(.+)\]( <=> (.+))?', r'\1', concept)
    listobjects = objects.split(', ')
    return stablestate in listobjects

def writeFinalFile(path, dict_assoc, list_wt, ens_obj):
    """ Write on a file the signature with associated stable states """

    input_file = path+'/Inputs_FP.tsv'
    if os.path.isfile(input_file) :
        df_input = pd.read_csv(input_file, sep='\t')
        try:
            df_input.insert(1, "Class", "")
        except ValueError :
            pass
    else : df_input = pd.DataFrame()
    # if "class" column already exists


    dict_wt = {}
    list_pheno = []
    f_out = open(path+'/AssociationPheno.txt', 'w')
    for protein, stable_state in dict_assoc.items():
        if protein == '': list_protein = []
        else : list_protein = protein.split(',')
        for sign in list_wt:
            if sign[1] == list_protein:
                name = sign[0]
        f_out.write('La signature de '+name+' : '+str(protein)+'\n')
        pheno = [sign[1] for sign in list_wt if sign[1] == list_protein]
        dict_wt[str(pheno[0])] = stable_state
        f_out.write('Les etats stables associes : '+'/'.join(stable_state)+'\n')
        f_out.write('')
        list_pheno.extend(stable_state)

        if not df_input.empty:
            for FP in stable_state:
                classes = df_input.loc[df_input['Name'] == FP, "Class"].values[0]
                lst_classes = classes.split('/')
                if name not in lst_classes:
                    df_input.loc[df_input['Name'] == FP, 'Class'] = classes+name+'/'
    f_out.write('\n')
    list_rest = [elem for elem in ens_obj if elem not in list_pheno]
    f_out.write('Les etats qui ne sont pas associes : '+'/'.join(list_rest)+'\n')
    f_out.close()

    if not df_input.empty: df_input.to_csv(input_file, sep='\t', index=False)

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
    #commun = DataFrame(list_commun, index=list_SS, columns=list_pheno)
    #drawheatmap(commun, "Pourcentage de marqueurs en commun", path)
    #    diff = DataFrame(list_distance, index=list_SS, columns=list_pheno)
    #    drawheatmap(diff, "Distance = distance entre les protéines exprimées", path)

styles = {
    'graph': {
        'fontsize': '14',
        'fontcolor': '#333333',
        'bgcolor': 'white',
        #'rankdir': 'BT' met le treillis a l'envers,
    'ratio': '0.8',
    },
    'nodes': {
        'fontname': 'Helvetica',
        #'shape': 'hexagon',
        'fontcolor': '#006699',
        'color': '#333333',
        'style': 'filled',
        'fillcolor': 'white',
    },
    'edges': {
        #'style': 'dashed',
        'color': '#333333',
        'arrowhead': 'open',
        'fontname': 'Courier',
        'fontsize': '14',
        'fontcolor': '#333333',
    }
}
def apply_styles(graph, styles):
    graph.graph_attr.update(
        ('graph' in styles and styles['graph']) or {}
    )
    graph.node_attr.update(
        ('nodes' in styles and styles['nodes']) or {}
    )
    graph.edge_attr.update(
        ('edges' in styles and styles['edges']) or {}
    )
    return graph

def searchVariant(dict_class, list_wt, data_matrix, path):

    if not os.path.exists(path+'/Variants'):
        os.makedirs(path+'/Variants')

    for sign in list_wt:
        matrix = {}
        with open(path+"/Variants/Variant"+sign[0]+".tsv", 'w') as variantFile:
            key = ','.join(sign[1])
            for obj in dict_class[key]:
                matrix[obj] = data_matrix[obj]
            sub_concept = dictToConcept(matrix)
            sub_lattice = sub_concept.lattice
            variantFile.write("Number of Variants: " + str(len(sub_lattice)) + "\n")
            variantFile.write('Signature of variant\tNumber of stable states\n')
            for extent, intent in sub_lattice:
                if extent != () :
                    variantFile.write('%r\t%r\n' % (intent, len(extent)))
            variantFile.write("\n")
            graphe = sub_lattice.graphviz()
            graphe = apply_styles(graphe, styles)
            graphe.render(filename=path+"/Variants/Variant"+sign[0], cleanup=True)


def analysisByBorne(file_csv, file_result, file_sign, path):
    """ Association of steady stable states with phenotype describing by the WT """
    start = time.time()
    #print("start")
    list_wt = []

    ''' Create a dict for the signature {'name of signature' : [signature's proteins]} '''
    dico_wt = RS.researchSignature(file_csv, file_sign)
    for name, sign in dico_wt.items():
        list_wt.append((name, sign))
    #print(list_wt)

    ''' Create a matrix with all fix points and their expressed proteins '''
    data_matrix = readMatrixFCA(file_csv)
    #print("matrix created")

    ''' Pass the matrix onto a FCA context '''
    context = dictToConcept(data_matrix)
    #print("lattice created")
    #bottom = lattice.infimum


    ''' Definition of all properties within formal context '''

    # all_objects = c.objects  # row of context
    all_attributes = context.properties # column of context
    #print(all_attributes)
    # intent = c.intension() # common attributes to list of object
    # extent = c.extension() # common objects to list of attribute
    # concept = c[]  # closest concept matching intent/extent : can be the supremum or infinum ==> __getitem__ can be use to
    # supremum = c[all_objects]
    # infinum = c[all_attributes]

    all_objects = list(context.objects)
    #print(all_objects)


    dict_assoc = {}
    list_concept_mutation = []

    ''' Give a list of all signature : [(protein expressed in signature 1), (protein expressed in signature 2)...] '''
    list_signature = [sign[1] for sign in list_wt]
    #list_signature.sort(key=lambda x: len(x), reverse=True)
    if ['neither'] in list_signature: list_signature.append(list_signature.pop(list_signature.index(['neither'])))
    #print(list_signature)


    ''' Create a dict which represents the association between signature and fix points {'signature's proteins' : [list of fix points associated]} '''
    for pheno in list_wt:
        dict_assoc[','.join(pheno[1])] = []
        list_concept_mutation.append((pheno[1],[]))

    #print("association started")

    #start_FP = 0
    #seuil = 1


    dict_mutant = readMatrix(file_result)
    for fix_point, mutation_name in dict_mutant.items():
        #print(fix_point)
        # if there is several mutations for one stable state
        if len(mutation_name) > 1:
            mutation_name = [mutation_name[0]]
        mutations = mutation_name[0].split(', ')

    # If one of the signature is the absent in the other signatures [neither]
        no_signature = fix_point

    # Form of formal concept (FC) : [Prot1, Prot2 ...] --> The list of proteins in each signature

        for FC in list_signature :
            #print(FC)
            intent = []
            list_index = []         # If KO mutation(s), get the list of protein's index in FC which are absent in the signature concept
            for mut in mutations:
                if mut[-2:] == 'E1' and mut[:-3] not in list(FC):
                    intent.append(mut[:-3])
                if mut[-2:] == 'KO' and mut[:-3] in list(FC):
                    index = FC.index(mut[:-3])
                    list_index.append(index)
            if FC == ['empty']:
                att_fixpoint = context.intension([fix_point])
                if list(att_fixpoint) == intent:
                    dict_assoc[','.join(FC)].append(fix_point)
            elif FC == ['neither']:
                ''' If fix point is not associated ==> association with the signature () '''
                if no_signature:
                    #print(fix_point)
                    dict_assoc[','.join(FC)].append(fix_point)
            else:
                #print(FC)
                if set(FC).issubset(set(all_attributes)):
                    for i, prot in enumerate(FC):
                        if i not in list_index:
                            intent.append(prot)



                    ''' Looking for the closest concept matching given intent : signature concept under mutation (= concept) ==> tuple ({objects},{attributes}) '''
                    concept = context.__getitem__(intent)
                    objects = concept[0]
                    if fix_point in objects:
                        dict_assoc[','.join(FC)].append(fix_point)

                        ''' Fix point is associated so no need to be associated with the neither signature '''
                        no_signature = ''


    ''' dict_assoc is the dictionnary with the canonical ("pure") signature. We need to highlight the
    possible hybrid : function extractHybride(canonical_dict)

    dict_final is a dictionnary with protein signature as key and fixed points as value.
    list_wt is a list of all signatures (pure and hybrid) : [('Name', [proteins signature]), ...]
    '''

    #print(dict_assoc)

    dict_final = extractHybride(dict_assoc)
    #print(dict_final)
    signatures = [x[0] for x in list_wt]
    prot_sign = [x[1] for x in list_wt]

    for key in list(dict_final):
        if key.split(',') in prot_sign : continue ## canonical signature
        hybrid_name = []
        st = set(key.split(','))
        for i, prot in enumerate(prot_sign):
            # print(set(prot))
            # print(st)
            # print(set(prot).issubset(st))
            if set(prot).issubset(st) : hybrid_name.append(signatures[i])
        list_wt.append(('_'.join(hybrid_name), key.split(',')))


    searchVariant(dict_final, list_wt, data_matrix, path)


    #print(list_wt)

                    # for elem in list_concept_mutation:
                    #    if elem[0] == list(FC):
                    #        elem[1].append(mutation_name)
                    #print(type(concept))

 # if attribute of formal concept is empty

                # for mut in mutations:
                #     if mut[-2:] == 'E1':
                #         intent.append(mut[:-3])

                # concept = context.__getitem__(intent)
                # objects = concept[0]
                # if fix_point in objects:
                #     dict_assoc[FC].append(fix_point)

            # print(empty_FC)




    list_rest, dico_wt = writeFinalFile(path, dict_final, list_wt, all_objects)

    #print("Time (sec) : "+str(time.time()-start))
analysisByBorne(file_csv, file_result, file_sign, path)
