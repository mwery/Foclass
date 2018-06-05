#! /usr/bin/env python3

"""
Take results from Python analysis as input and give Aurelien Naldi's type of table (protein by fix point according to each phenotype)
==> Heatmap : row is mutation name + value of fix points associated & column is protein name

and Elisabeth Remy's type of table
==> Table : row is mutation name and column is classe name

@author : Méline WERY
@mail : meline.wery@irisa.fr

"""

import sys
import os
import re
import csv
import ast
import time

from math import ceil


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import ListedColormap
import pygraphviz as pgv

from scipy.spatial.distance import pdist
from scipy.cluster.hierarchy import linkage, dendrogram
from mpl_toolkits.axes_grid1 import make_axes_locatable

import concepts # https://pypi.python.org/pypi/concepts
from concepts import Context
from concepts import Definition


if len(sys.argv) == 2:
    folder = sys.argv[1]

current_path = os.getcwd()+'/'+folder
#print(current_path)
file = current_path+"/AssociationPheno.txt"
prot_file = current_path+"/matricemutantProtTab.csv"
mut_file = current_path+"/matricemutantWTKOE1Tab.csv"
result_folder = current_path+"/AssocResultPython/"

if not os.path.exists(result_folder):
    os.makedirs(result_folder)

styles = {
    'graph': {
        'fontsize': '10',
        'fontcolor': '#333333',
        'bgcolor': 'white',
        #'rankdir': 'BT', #met le treillis a l'envers,
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
        'fontsize': '6',
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

def classbymutation(dict, list_mut, result_folder):
    list_class = list(dict.keys())
    mutations_row = []

    for mutation in list_mut:
        mutations_row.append((mutation,[0]*len(list_class)))
    col_width = 0
    d = concepts.Definition()
    for clas,value in dict.items():
        if col_width < len(clas) : col_width = len(clas)

        d.add_object(clas, value[1])

        for val in value[1]:
            for elem in mutations_row:
                if elem[0] == val:
                    i = list_class.index(clas)
                    elem[1][i] = 1

    c = concepts.Context(*d)
    l = c.lattice
    graphe = l.graphviz()
    graphe = apply_styles(graphe, styles)
    graphe.render(filename=result_folder+"Treillis", cleanup=True)

    list_object = []
    list_attribute = []
    maxi = 0
    for extent, intent in c.lattice:
        if len(extent) > maxi: maxi=len(extent)
        list_object.append(extent)
        list_attribute.append(intent)
    list_attribute = overlap(list_object, list_attribute, maxi)

    rest_combination = []
    specifyFile = open(result_folder+"Class_Specific_Mutations.txt", "w")
    for i, elem in enumerate(list_object):
        if len(elem) == maxi:
            specifyFile.write("All classes can be achieved by those mutations :\n")
            specifyFile.write("  /  ".join(list_attribute[i])+"\n\n")
        elif len(list_attribute[i]) == 0:
            rest_combination.append(elem)
            pass
        else:
            specifyFile.write("Only "+str(elem)+" can be achieved by those mutations :\n")
            specifyFile.write("  /  ".join(list_attribute[i])+"\n\n")
    specifyFile.write("Other combination of class don't have specific mutations :\n")
    for rest in rest_combination:
        specifyFile.write(str(rest)+" ")


    df = pd.DataFrame.from_items(mutations_row, orient='index', columns=list_class)
    df.sort_index(inplace=True)

    with open(result_folder+"result.tex", 'w') as latex_file:
        latex_file.write(r'''\documentclass[10pt,a4paper,landscape]{article}
            \usepackage[left=1.5cm, right=1.5cm, top=1.5cm, bottom=1.5cm]{geometry}
            \usepackage{array}
            \usepackage{booktabs}
            \usepackage{longtable}
            \begin{document}
            ''')
        p = 'p{4cm}|'
        #print(p) , col_space=10
        col_format = '|p{5cm}|'+ 'c|'*len(list_class)
        latex_file.write(df.to_latex(column_format=col_format, longtable=True))
        latex_file.write('''
            \end{document}
            ''')
    os.system('pdflatex -output-directory={} result.tex > /dev/null'.format(result_folder))

def drawMultiplot(df, title, maxi):


    max_row = 60

    sub_df = []
    begin = 0
    end = max_row
    page = 1

        #print(data)
    with PdfPages(title+'.pdf') as pdf:
        plt.rcParams.update({'figure.max_open_warning': 0})
        total_plot = len(df)
        fig = plt.figure()

        for i,elem in enumerate(df):
            ax = fig.add_subplot(total_plot,1,i+1)
            divider = make_axes_locatable(ax)
            #cax = divider.append_axes('right', size='5%', pad=0.05)
            im = ax.imshow(elem, interpolation='none', cmap=plt.cm.Greys, vmin=0, vmax=maxi, aspect="auto")
            #fig.colorbar(im, ticks=list(range(0, maxi+1)))
            ax.yaxis.tick_right()
            ax.set_yticks(range(elem.shape[0]))
            ax.set_ylabel((elem.index)[0], size=6, rotation='horizontal', labelpad=30)
            ax.yaxis.set_label_position('left')
            ax.yaxis.set_ticks_position('left')
            ax.set_yticklabels([])
            ax.invert_yaxis()
            if i == 0:
                #matrix_width = (20 * elem.shape[1])/72.27
                #figure_width = matrix_width / (1 - 0.4 - 0.4)
                #fig.set_size_inches(figure_width, fig.get_figheight(), forward=True)

                ax.set_xticks(range(elem.shape[1]))
                ax.set_xticklabels(elem.columns, size=6, rotation='vertical')
                ax.xaxis.set_ticks_position('top')
            else:
                ax.xaxis.set_visible(False)

        cax = fig.add_axes([0.9, 0.1, 0.03, 0.8])
        fig.colorbar(im, cax=cax, ticks=list(range(0, maxi+1)))
        #plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)
        #plt.gcf().subplots_adjust(bottom=0.30)
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

def drawMultipage(df, pdf, maxi):

        plt.rcParams.update({'figure.max_open_warning': 0})

        ''' Fix height for each cell according to ylabel ticks '''

        #print(df)
        if df.empty : return plt
        # comput the matrix height in inch
        #print("tata")
        #print(df.shape[0])
        matrix_height = (20 * df.shape[0])/72.27
        matrix_width = (20 * df.shape[1])/72.27
        #print(matrix_height)
        #print(matrix_width)
        # compute the required figure height
        top_margin = 0.25  # in percentage of the figure height
        bottom_margin = 0.2 # in percentage of the figure height
        figure_height = matrix_height / (1 - top_margin)
        figure_width = matrix_width / (1 - top_margin - bottom_margin)

        fig, ax = plt.subplots(figsize=(matrix_width, matrix_height), dpi=300)

        divider = make_axes_locatable(ax)
        cax = divider.append_axes('right', size='5%', pad=0.05)

        im = ax.imshow(df, interpolation='none', cmap=plt.cm.Greys, vmin=0, vmax=maxi)
        fig.colorbar(im, cax=cax, ticks=list(range(0, maxi+1)))

        ax.yaxis.tick_right()
        ax.set_yticks(range(df.shape[0]))
        ax.set_xticks(range(df.shape[1]))
        ax.set_xticklabels(df.columns, size=6, rotation='vertical')
        ax.set_yticklabels(df.index, size=6)
        ax.xaxis.set_ticks_position('top')
        ax.yaxis.set_ticks_position('left')
        ax.invert_yaxis()

        try:
            plt.tight_layout()
            pdf.savefig(fig)  # saves the current figure into a pdf page


        except ValueError :
            bbox = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
            width, height = bbox.width, bbox.height
            new_height = figure_height + 4*height
            fig.set_size_inches(matrix_width, new_height)
            plt.tight_layout()

            pdf.savefig(fig, dpi=300)  # saves the current figure into a pdf page


        return plt

        #plt.clf()
        #plt.close()  #bbox_inches='tight'

def drawheatmap(data, title, maxi):

    max_row = 60

    sub_df = []
    begin = 0
    end = max_row
    page = 1
    with PdfPages(title+'.pdf') as pdf:
        while (True):
            if end < data.shape[0]:
                sub_df = data[begin:end]
                drawMultipage(sub_df, pdf, maxi)
                begin = begin + max_row
                end = end + max_row
            else:
                end = data.shape[0]
                sub_df = data[begin:end]
                drawMultipage(sub_df, pdf, maxi)

                break

    #print('')


def drawclusthier(data, title, maxi):

    matrix_height = (20 * data.shape[0])/72.27
    matrix_width = (10 * data.shape[1])/72.27
    #print(matrix_height)
    #print(matrix_width)
    # compute the required figure height
    top_margin = 0.2  # in percentage of the figure height
    bottom_margin = 0.2 # in percentage of the figure height
    figure_height = matrix_height / (1 - top_margin - bottom_margin)
    figure_width = matrix_width / (1 - top_margin - bottom_margin)

    #plt.figure(figsize=(matrix_width, matrix_height), dpi=300)

    main_axes = plt.gca()
    divider = make_axes_locatable(main_axes)
    # 1.0, pad=0
    plt.sca(divider.append_axes("left", 1.0, pad=0))
    ylinkage = linkage(pdist(data, metric='euclidean'), method='average', metric='euclidean')
    ydendro = dendrogram(ylinkage, orientation='left', no_labels=True, distance_sort='descending', no_plot=True)
    plt.gca().set_axis_off()
    data = data.ix[[data.index[i] for i in ydendro['leaves']]]

    plt.sca(main_axes)
    plt.imshow(data, aspect='auto', interpolation='none', cmap=plt.cm.Blues)
    plt.colorbar(pad=0.15, ticks=list(range(0, maxi+1)))
    plt.gca().yaxis.tick_right()
    plt.yticks(range(data.shape[0]), data.index, size=6)
    plt.xticks(range(data.shape[1]), data.columns, size=6, rotation='vertical')
    plt.gca().xaxis.set_ticks_position('none')
    plt.gca().yaxis.set_ticks_position('right')
    plt.gca().invert_yaxis()

    plt.tight_layout()

    #plt.show()
    plt.savefig(title+'.pdf')
    plt.clf()


def clusthier(dict, list_prot, result_folder):
    """ Make an heatmap with fix points characterised by mutations as row and protein expressed as column """

    folder = result_folder+'HeatmapByPheno/'
    if not os.path.exists(folder):
        os.makedirs(folder)

    for classe,value in dict.items():
        #print(classe)
        #print(value[0])
        list_proteinvalue = value[0]
        if list_proteinvalue == []:
            #print("non")
            continue
        row = []
        max_value = 0
        for elem in list_proteinvalue:
            if max(elem[1:]) > max_value: max_value = max(elem[1:])
            row.append((elem[0], elem[1:]))


        data = pd.DataFrame.from_items(row, orient='index', columns=list_prot)
        #data.sort_index(inplace=True)
        #print(data)
        if len(data) > 1 : drawclusthier(data.transpose(), folder+'ClustHier'+classe, max_value)

def heatmapclass(dict, list_prot, result_folder):
    """ Make an heatmap with fix points characterised by mutations as row and protein expressed as column """

    folder = result_folder+'HeatmapByPheno/'
    if not os.path.exists(folder):
        os.makedirs(folder)

    for classe,value in dict.items():
        #print(classe)
        #print(value[0])
        list_proteinvalue = value[0]
        if list_proteinvalue == []:
            #print("non")
            continue
        row = []
        max_value = 0
        for elem in list_proteinvalue:
            if max(elem[1:]) > max_value: max_value = max(elem[1:])
            row.append((elem[0], elem[1:]))


        data = pd.DataFrame.from_items(row, orient='index', columns=list_prot)
        #data.sort_index(inplace=True)
        drawheatmap(data, folder+'FixPoints'+classe, max_value)
        #plt.close()
        #print(data)
def heatmapmut(dict, list_prot, result_folder):
    """ Make an heatmap with fix points characterised by class as row and protein expressed as column """

    folder = result_folder+'HeatmapByMut/'
    if not os.path.exists(folder):
        os.makedirs(folder)

    for mutation,list_proteinvalue in dict.items():
        #print(mutation)
        #print(list_proteinvalue)
        list_data = []
        max_value = 0
        set_class = {x[0] for x in list_proteinvalue}
        for clas in set_class:
            row = []
            max_value = 0
            list_value = [x for x in list_proteinvalue if x[0]==clas]
            for elem in list_value:
                if max(elem[1:]) > max_value: max_value = max(elem[1:])
                row.append((elem[0], elem[1:]))
            data = pd.DataFrame.from_items(row, orient='index', columns=list_prot)
            data.sort_index(inplace=True)
            list_data.append(data)
        drawMultiplot(list_data, folder+'FixPoints'+mutation, max_value)

def heatmapuncl(liste, list_prot, folder):
    """ Make an heatmap with all fix points not classified, mutation as row and protein expressed as column """

    row = []
    max_value = 0
    for state in liste:
        if max(state[1:]) > max_value: max_value = max(state[1:])
        row.append((state[0], state[1:]))

    data = pd.DataFrame.from_items(row, orient='index', columns=list_prot)
    data.sort_index(inplace=True)
    drawheatmap(data, folder+'UnclassifiedFixPoints', max_value)

def overlap(signature, fixpoints, maxi):
    """ Compare each set of fix points to avoid the presence of one fix point into several phenotype """

    for j, current in enumerate(signature):
        if len(current) == maxi:
            for i, test in enumerate(signature):
                if len(test) < len(current) :
                    if set(test).issubset(set(current)):
                        fixpoints[i] = [e for e in fixpoints[i] if e not in fixpoints[j]]

    if maxi > 1:
        maxi = maxi - 1
        return overlap(signature, fixpoints, maxi)
    else :
        return fixpoints

def main(file, protfile, mutfile, result_folder):
    """ Parse the association file to get a dict with for each phenotype as key, the value is a list of 2 lists [[all fix points and their values],[all mutations]]

    {'class name' : [list of fix points + value], [list of mutations associated]
    ...}

    """
    start = time.time()
    dict_class = {}

    prot_df = pd.read_csv(protfile)
    prot_df = prot_df.set_index(['Name'])
    mut_df = pd.read_csv(mutfile)
    mut_df = mut_df.set_index(['Name'])

    ''' Pass from column = proteins & row = fix points To column = fix points & row = proteins '''

    rev_prot_df = prot_df.T
    header = list(prot_df)       #header = list of proteins
    rev_mut_df = mut_df.T

    ''' Get for each phenotype, a list of all the fix points '''

    list_sign = []
    all_state = []
    list_name = []              # List of signature
    with open(file, 'r') as f_in:
        for line in f_in:
            if line.startswith("La signature"):
                name = re.sub(r'La signature de (.+) : (.+)\n', r'\1', line)         # name = phenotype name
                sign = re.sub(r'La signature de (.+) : (.+)\n', r'\2', line)
                sign = sign.split(',')

                next_line = f_in.readline()
                liste = re.sub(r'Les etats stables associes :(.+)', r'\1', next_line)
                if liste == '\n':                                           # if there is no associated fix points for a signature
                    list_state = []
                else :
                    list_state = liste.strip().split('/')                               # list of fix points

                list_name.append(name)
                list_sign.append(sign)
                all_state.append(list_state)
            if line.startswith("Les etats qui ne sont pas"):
                unclass_state = line.split(':')[1].strip()
                unclass_state = unclass_state.split('/')

    list_mutation = []
    dict_mut = {}
    for i, name in enumerate(list_name):            # name = signature
        #print(name)
        list_state = all_state[i]
        #print(list_state)
        dict_class[name]=[[],[]]
        l = dict_class.get(name)
        for FP in list_state:
            if FP:
                state = FP.strip('()').upper()
                #print(state)

                value = rev_prot_df[state].tolist()
                #print(value)
                #print(state)

                mutations = rev_mut_df[rev_mut_df[state] == 1].index.tolist()

                ''' If we want to check each mutation, even if some lend to a WT fix points : use only first paragraph '''
                for mut in mutations:
                    if mut not in list_mutation:
                        list_mutation.append(mut)

                    ''' Increase the dict_class : {'Name of signature' : [[lists of FP value with mutation], [list of FP mutation]]} '''
                    if FP:

                        ''' If we want to combine all mutations with the WT fix points : add this paragraph to the code '''
                        # else:
                        #     value_copy = list(value)
                        #     value_copy.insert(0,'WT')
                        #     l[0].append(value_copy)

                        #     if 'WT' not in l[1]:
                        #         l[1].append('WT')
                        #     if 'WT' not in list_mutation:
                        #         list_mutation.append('WT')


                        value_copy = list(value)
                        value_copy.insert(0,mut)
                        l[0].append(value_copy)         # for each mutation type, append values of proteins
                    if mut not in l[1]:
                        l[1].append(mut)
                    #print(dict_class)


                    ''' Increase the dict_mut : {'Mutation' : [lists of FP value with name]} '''

                    if FP:

                        ''' If we want to group the mutation that lead to the same FP than WT, untoggle this part '''

                        # if state.startswith('WT'):
                        #     value_cop = list(value)
                        #     value_cop.insert(0,name)
                        #     if 'WT' not in dict_mut:
                        #         dict_mut['WT'] = []
                        #         dict_mut['WT'].append(value_cop)
                        #     else:
                        #         dict_mut['WT'].append(value_cop)
                        #else:

                        value_cop = list(value)
                        value_cop.insert(0,name)
                        if mut not in dict_mut:
                            dict_mut[mut] = []
                            dict_mut[mut].append(value_cop)
                        else:
                            dict_mut[mut].append(value_cop)
                        #print(dict_mut)


    #print(list_mutation)

    classbymutation(dict_class, list_mutation, result_folder)

    ''' One Heatmap by class '''
    clusthier(dict_class, header, result_folder)

    heatmapclass(dict_class, header, result_folder)
    print("Heatmap per class done.")

    ''' One Heatmap by mutation '''
    heatmapmut(dict_mut, header, result_folder)
    print('Heatmap per mutation done.')

    #print(unclass_state)
    list_unclass = []
    if unclass_state != ['']:
        for state in unclass_state:
            value = rev_prot_df[state].tolist()
            mutations = rev_mut_df[rev_mut_df[state] == 1].index.tolist()
            for mut in mutations:
               value_copy = list(value)
               value_copy.insert(0, mut)
               list_unclass.append(value_copy)

        ''' One Heatmap for all unclassified fix points '''
        heatmapuncl(list_unclass, header, result_folder)
        print("Heatmap for unclassified done.")


main(file, prot_file, mut_file, result_folder)
