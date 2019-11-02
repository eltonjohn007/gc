# -*- coding: utf-8 -*-
"""
Created on Fri Jan  4 01:26:59 2019

@author: elton
"""
#import csv
#digit16file='data/16digit.csv'
#digit16brand=[]
#with open(digit16file) as f:
#    read=csv.reader(f,delimiter=',')
#    for row in read:
#        digit16brand.append(row[0])
#    digit16brand.sort()
#digit19file='data/19digit.csv'
#digit19brand=[]
#with open(digit19file) as f:
#    read=csv.reader(f,delimiter=',')
#    for row in read:
#        digit19brand.append(row[0])
#    digit19brand.sort()
#codeonlyfile='data/codeonly.csv'
#codeonlybrand=[]
#with open(codeonlyfile) as f:
#    read=csv.reader(f,delimiter=',')
#    for row in read:
#        codeonlybrand.append(row[0])
#    codeonlybrand.sort()
#def brandprocessing(x,y):
#    codeonly=False
#    if x in digit16brand:
#        y=y[-16:]
#    if x in digit19brand:
#        y=y[-19:]
#    if x=='lord and taylor':
#        y=y[-10:]
#    if x=='target':
#        y=y[:15]
#    return y
#def codeonly(x):
#    return x in codeonlybrand

import pandas as pd
df=pd.read_csv('data/brand.csv').T
df.columns=df.iloc[0]
df=df[1:]

def brandprocessing(x,y):
    if not pd.isna(df[x]['digits']):
        digits=df[x]['digits']
        if digits[-1]=='e':
            y=y[-int(digits[:-1]):]
        elif digits[-1]=='f':
            y=y[0:int(digits[:-1])]
    return y

def codeonly(x):
    return not pd.isna(df[x]['codeonly'])