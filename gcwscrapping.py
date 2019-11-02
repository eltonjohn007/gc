# -*- coding: utf-8 -*-
"""
Created on Tue Feb 12 15:15:48 2019

@author: Yechao
"""

import datetime
import pandas as pd
directory=directory='data/gcdata.csv'
df=pd.read_csv(directory)

def findsource(brand,code):
    df1=df[(df['Brand']==brand) & (df['Code'].str.contains(code))]
    if df1.shape[0]==1:
        return df1.loc[df1.index.values[0]]['Source']
    else:
        return ''
def process():
    datasource=input('Enter data source \'web\',\'email\': ')
    sourcebool=input('Do you need to find out the source? ')
    if sourcebool=='y':
        brand=input('Enter brand: ')
    newdatalist=[]
    if datasource=='web':
        data=input('Enter gcw data: ')
        datalist=[x.split('\t') for x in data.split('\n')]
        datadict={}
        for x in datalist:
            day=int(x[-2][:-2])
            d=(datetime.datetime.today()-datetime.timedelta(days=day)).strftime('%Y-%m-%d')
            soldprice='$'+str(float(x[4][1:])+float(x[5][1:]))
            y=[x[0],d,x[1],soldprice]
            if sourcebool=='y':
                y.append(findsource(brand,x[2]))
            else:
                y.append('')
            z=','.join(y)
            if z not in datadict:
                datadict[z]=1
            else:
                datadict[z]+=1
        for (key,value) in datadict.items():
            newdatalist.append(key.split(',')[:-1]+[value,key.split(',')[-1]])
    elif datasource=='email':
        datalist=[]
        counter=True
        while counter:
            data=input('Enter gcw data: ')
            if data!='':
                datalist.extend([x.split('\t') for x in data.split('\n')])
            else:
                counter=False
        datadict={}
        for x in datalist:
            if x[2] not in datadict:
                datadict[x[2]]=[x[0],float(x[1][1:]),float(x[3][1:]),x[4][:10]]
            else:
                datadict[x[2]][2]+=float(x[3][1:])
        for x in datadict:
            datadict[x]=datadict[x][0]+','+datadict[x][3]+','+'$'+str(datadict[x][1])+','+'$'+str(datadict[x][2])
        datadict2={}
        for (key,value) in datadict.items():
            newkey=value+','+key
            if newkey not in datadict2:
                datadict2[newkey]=1
            else:
                datadict2[newkey]+=1
        for (key,value) in datadict2.items():
            keysplit=key.split(',')
            if sourcebool=='y':
                newdatalist.append(keysplit[:-1]+[value,findsource(brand,keysplit[-1])])
            else:
                newdatalist.append(keysplit[:-1]+[value,''])
    newdatalist=sorted(newdatalist,key=lambda x:(x[0],x[1]))
    header=['brand','date','price','sell','count','source']
    dash='-'*70
    print('\n')
    print(dash)
    print('{:<20s}{:<13s}{:<8s}{:<9s}{:<10s}{:<15s}'.format(header[0],header[1],header[2],header[3],header[4],header[5]))
    print(dash)
    for i in range(len(newdatalist)):
        print('{:<20s}{:<13s}{:<8s}{:<9s}{:<10d}{:<5s}'.format(newdatalist[i][0],newdatalist[i][1],newdatalist[i][2],newdatalist[i][3],newdatalist[i][4],newdatalist[i][5]))

process()