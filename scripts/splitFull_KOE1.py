#! /usr/bin/env python3
# -*- coding: utf-8 -*-
""" Parse the matricemutantFullTab file into 3 main files:
    FormalContext
    FormalContextMutationKOE1
    FormalContextMutationWTKOE1
@author : Meline WERY
"""
import pandas as pa
import sys, os

if len(sys.argv) == 2:
    filepath = sys.argv[1]
    path = os.path.dirname(filepath)

def MatrixSplitKOE1(filepath):
    """ Function to parse matriceFull """

    df = pa.read_csv(filepath, sep=',', error_bad_lines=False)
    index_name = list(df.columns).index('Name')
    index_wt = list(df.columns).index('WT')
    liste_protein = df.drop(df.columns[index_wt:], axis=1)
    liste_protein = liste_protein.set_index('Name')
    liste_protein.to_csv(path+'/FormalContext.csv', sep=',', encoding='utf-8')
    liste_wt = df.drop(df.columns[index_name+1:index_wt], axis=1)
    liste_wtkoe1 = liste_wt.set_index('Name')
    liste_wtkoe1.to_csv(path+'/FormalContextMutationWTKOE1.csv', sep=',', encoding='utf-8')
#
    liste = df.drop(df.columns[index_name+1:index_wt+1], axis=1)
    liste_koe1 = liste.set_index('Name')
    liste_koe1.to_csv(path+'/FormalContextMutationKOE1.csv', sep=',', encoding='utf-8')

MatrixSplitKOE1(filepath)
