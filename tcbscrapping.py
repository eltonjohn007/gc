# -*- coding: utf-8 -*-
"""
Created on Thu Feb 28 17:57:28 2019

@author: elton
"""

from datetime import datetime

def process():
    paymentperiod=input('Enter next payment periods: ')
    start=input('Count start date?')
    submissiondates=[x.split()[0] for x in paymentperiod.split('PT\t')][:2]
    date1=datetime.strptime(submissiondates[0],'%m/%d/%Y')
    date2=datetime.strptime(submissiondates[1],'%m/%d/%Y')
    
    gcdata=input('Enter gc submissions: ')
    gcdata=gcdata.replace('Processed','Confirmed')
    #split submissions
    gcdata1=gcdata.split('Confirmed')
    #filter submissions that have not been paid
    gcdata2=[x.split('\n') for x in gcdata1[1:] if 'No' in x]
    for n,x in enumerate(gcdata2):
        gcdata2[n]=[y for y in x if y!='']
    #(payout,submission date) for each submission
    gcdata3=[(float(x[12][1:]),x[2].split()[0]) for x in gcdata2]
    payment=0
    for x in gcdata3:
        date=datetime.strptime(x[1],'%Y-%m-%d')
#        if date1<=date<=date2:
        if start=='':
            if date<=date2:
                #add payout if it falls before the cutoff date
                payment+=x[0]
        else:
            if date<=date2 and date>=date1:
                payment+=x[0]
    print('Total payment:',payment)
    f=open('D:/Dropbox (MIT)/Documents/tcb payment.txt','w')
    f.write(str(payment))
    f.close()
process()