
import requests
from bs4 import BeautifulSoup
import re
import csv
import datetime
import pandas as pd

import pdfkit
path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
options={'quiet':''}

#detect if source is in right format
sourcefile='data/source.csv'
df=pd.read_csv('data/brand.csv').T
df.columns=df.iloc[0]
df=df[1:]

df2=pd.read_csv('data/brand.csv')

class ss():
    def sourcelist():
        sourcelist=[]
        with open(sourcefile) as f:
            read=csv.reader(f,delimiter=',')
            for row in read:
                sourcelist.append(row[0])
        sourcelist.sort()
        return sourcelist
    def contain(x):
        return x in ss.sourcelist()
    def add(x):
        if not ss.contain(x):
            with open(sourcefile,'a',newline='') as f:
                writer = csv.writer(f)
                writer.writerow([x])
            print('\nSource added')
        else:
            print('\nSource already included!')
#detect if brand is in right format
class bb():
    def brandlist():
        brandlist=list(df2['brand'])
        brandlist.sort()
        return brandlist
    def contain(x):
        return x in bb.brandlist()

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

def savedir():
    return 'D:\\Dropbox (MIT)\\Documents\\'+datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")+'.pdf'
#compile gcdata into desired format for output and storage
def gccompile():
    if gcformat=='1':
        if not codeonly(brand):
            gcdata.append([datetime.datetime.now().strftime("%Y-%m-%d"),source,brand,balance,'\''+code,'\''+pin])
            gcprint.append(balance+','+code+','+pin)
        else:
            gcdata.append([datetime.datetime.now().strftime("%Y-%m-%d"),source,brand,balance,'\''+code])
            gcprint.append(balance+','+code)
    elif gcformat=='2':
        if not codeonly(brand):
            gcdata.append([datetime.datetime.now().strftime("%Y-%m-%d"),source,brand,balance,'\''+code,'\''+pin])
            gcprint.append(code+','+pin+','+balance)
        else:
            gcdata.append([datetime.datetime.now().strftime("%Y-%m-%d"),source,brand,balance,'\''+code])
            gcprint.append(code+',,'+balance)

def numonly(A):
    B=[l for l in A if l.isdigit() or l.isalpha()]
    return ''.join(B)
#gc directory
directory='D:\\Dropbox (MIT)\\Documents\\finance\\gift cards\\gcdata.csv'
#def process():
if 'gcinput' not in locals():
    gcinput=input('Enter input format (1 for url, 2 for gc codes, 3 for scanned codes): ')
    while gcinput not in {'1','2','3'}:
        print('\nWrong format!')
        gcinput=input('Enter input format (1 for url, 2 for gc codes, 3 for scanned codes): ')

if 'gcformat' not in locals():
    gcformat=input('Enter format (1 for gcw, 2 for tcb): ')
    while gcformat not in {'1','2'}:
        print('\nWrong format!')
        gcformat=input('Enter format: ')
        
if 'source' not in locals():
    source=input('\nEnter source: ')
    while not ss.contain(source):
        possiblesource=[l for l in ss.sourcelist() if l[0]==source[0]]
        print(possiblesource)
        print('Possible sources. Did you enter wrongly?')
        source=input('Enter source: ')
            
if 'brand' not in locals():
    brand=input('\nEnter brand: ')
    while not bb.contain(brand):
        possiblebrand=[l for l in bb.brandlist() if l[0]==brand[0]]
        print(possiblebrand)
        print('Possible brands. Did you enter wrongly?')
        brand=input('Enter brand: ') 

if 'gcdata' not in locals():
    gcdata=[]
if 'gcprint' not in locals():
    gcprint=[]
#for url gc parsing
if gcinput=='1':
    if 'urlset' not in locals():
        urlset=set()
    if 'pagesave' not in locals():
        if gcformat=='1':
            pagesave=not pd.isna(df[brand]['gcwpdf'])
        if gcformat=='2':
            pagesave=not pd.isna(df[brand]['tcbpdf'])
#        printinput=input('Print gc page: ')
#        if printinput=='':
#            pagesave=False
#        else:
#            pagesave=True
            
    truth=True
    while truth:
        url=input('Enter url:')
        if url=='':
            truth=False
        elif url in urlset:
            print('\nDuplicate url!')
        else:
            page=requests.get(url)
            soup=BeautifulSoup(page.text,'html.parser')
            if 'paypal' in url:
                if pagesave:
                    try:
                        pdfkit.from_string(page.text,savedir(),configuration=config,options=options)
                    except:
                        pass
                text=soup.find('body').text
                balance=re.findall('\"itemValue\":\"(.+?)\"',text)[0][1:]
                if brand=='wayfair':
                    code=re.findall('\"security_code\":\"(.+?)\"',text)[0]
                else:
                    code=re.findall('\"card_number\":\"(.+?)\"',text)[0]
                code=brandprocessing(brand,code)
                if not codeonly(brand):
                    pin=re.findall('\"security_code\":\"(.+?)\"',text)[0]
            elif 'amazon' in url or 'activationspot' in url or 'sendgrid' in url or 'blackhawknetwork' in url or 'giftcardmall' in url or 'gianteagle' in url:
                if pagesave:
                    pdfkit.from_url(url,savedir(),configuration=config,options=options)
                text=soup.find('body').text
                if brand=='itunes':
                    balance=re.findall('Your (.+?) App Store',text)[0][1:]
                    code=re.findall('Card: (.+?)\n\n',text)[0]
                elif brand=='macy\'s':
                    balance=''.join([l for l in re.findall('\$(.+?)\n',text)[0] if l.isdigit()])
                    code=re.findall('Code\n\n\n(.+?)\n',text)[0].split(' ')[0]
                    pin=re.findall('Code\n\n\n(.+?)\n',text)[0].split(' ')[1]
                else:
                    if re.findall('\$(.+?)\n',text)!=[]:
                        balance=''.join([l for l in re.findall('\$(.+?)\n',text)[0] if l.isdigit()])
                    elif re.findall('your \$(.+?) USD',text)!=[]:
                        balance=re.findall('your \$(.+?) USD',text)[0]
                    if not balance.isdigit():
                        balance=''.join([l for l in balance if l.isdigit()])
                    if re.findall('Gift Card #: \n(.+?)\n',text)!=[]:
                        code=re.findall('Gift Card #: \n(.+?)\n',text)[0]
                    elif re.findall('#: (.+?)\n',text)!=[]:
                        code=re.findall('#: (.+?)\n',text)[0]
                    elif re.findall('Card: (.+?)\n',text)!=[]:
                        code=re.findall('Card: (.+?)\n',text)[0]
                    elif re.findall('Card Number: (.+?)\n',text)!=[]:
                        code=re.findall('Card Number: (.+?)\n',text)[0]
                    elif re.findall('Card #:\xa0\xa0(.+?)\n',text)!=[]:
                        code=re.findall('Card #:\xa0\xa0(.+?)\n',text)[0]
                    else:
                        code=re.findall('Card #:\n(.+?)\n',text)[0]
                    code=brandprocessing(brand,code).replace(' ','')
                    if not codeonly(brand):
                        if re.findall('Pin: (.+?)\n',text)!=[]:
                            pin=re.findall('Pin: (.+?)\n',text)[0]
                        elif re.findall('PIN\): (.+?)\n',text)!=[]:
                            pin=re.findall('PIN\): (.+?)\n',text)[0]
                        elif re.findall('PIN: (.+?)\n',text)!=[]:
                            pin=re.findall('PIN: (.+?)\n',text)[0]
                        elif re.findall('Pin:\n(.+?)\n',text)!=[]:
                            pin=re.findall('Pin:\n(.+?)\n',text)[0]
                        elif re.findall('PIN:\xa0\xa0(.+?)\n',text)!=[]:
                            pin=re.findall('PIN:\xa0\xa0(.+?)\n',text)[0]
                        elif re.findall('PIN\):\n(.+?)\n',text)!=[]:
                            pin=re.findall('PIN\):\n(.+?)\n',text)[0]
                        else:
                            pin=re.findall('Pin #: (.+?)\n',text)[0]
                        pin=pin.replace(' ','')
            elif 'vcdelivery' in url or 'newegg' in url:
                if pagesave:
                    pdfkit.from_url(url,savedir(),configuration=config,options=options)
                text=str(soup.find('body'))
                if re.findall('CardNumber": "(.+?)",\r',text)!=[]:
                    code=re.findall('CardNumber": "(.+?)",\r',text)[0]
                elif re.findall('CardNumber&quot;: &quot;(.+?)&quot;,\r',text)!=[]:
                    code=re.findall('CardNumber&quot;: &quot;(.+?)&quot;,\r',text)[0]
                elif re.findall('CBID=(.+?)&amp',text)!=[]:
                    code=re.findall('CBID=(.+?)&amp',text)[0]
                elif re.findall('Number: (.+?)\n',text)!=[]:
                    code=re.findall('Number: (.+?)\n',text)[0]
                else:
                    code=re.findall('id="lblCertBarCode"><br/>(.+?)</span>',text)[0]
                code=brandprocessing(brand,code)
                if not codeonly(brand):                
                    if re.findall('Pin": "(.+?)",\r',text)!=[]:
                        pin=re.findall('Pin": "(.+?)",\r',text)[0]
                    elif re.findall('Pin&quot;: &quot;(.+?)&quot;,\r',text)!=[]:
                        pin=re.findall('Pin&quot;: &quot;(.+?)&quot;,\r',text)[0]
                    else:
                        pin=re.findall('"lblPin">(.+?)</span>',text)[0]
                if re.findall('InitialBalance(.+?)\r',text)!=[]:
                    balance=''.join([l for l in re.findall('InitialBalance(.+?)\r',text)[0] if l.isdigit() or l=='.'])[:-5]
                else:
                    balance=''.join([l for l in re.findall('"lblCertAmount">(.+?)</span>',text)[0] if l.isdigit() or l=='.'])[:-3]
            elif 'cashstar' in url:
                if pagesave:
                    pdfkit.from_url(url,savedir(),configuration=config,options=options)
                text=soup.find('body').text
                balance=re.findall('\$(.+?) ',text)[0][:-3]
                code=re.findall('Card Number: \n\n\n(.+?)\n',text)[0]
                code=brandprocessing(brand,code)
                if not codeonly(brand):
                    pin=re.findall('Pin: (.+?)\n',text)[0]        
            gccompile()
            urlset.add(url)
            del page
            print('\n'+str(len(gcdata))+' card entered!')
#for physical gc parsing
elif gcinput=='2':
    balance=input('Enter gc balance: ')
    truth=True
    while truth:
        A=input('Enter gc code: ')
        if A=='':
            truth=False
        else:
            code=numonly(A)
            code=brandprocessing(brand,code)
            if not codeonly(brand):
                pin=input('Enter gc pin: ')
            gccompile()
        print('\n'+str(len(gcdata))+' card entered!')
#for scanned gc parsing
elif gcinput=='3':
    balance=input('Enter gc balance: ')
    data=input('Enter gc data: ')
    today=datetime.date.today().strftime("%m/%d/%Y")
    gccodes=[x.replace(' ','') for x in data.split('\n') if not x=='' and not today in x and not ':' in x]
    for l in gccodes:
        print('\n')
        code=brandprocessing(brand,l)
        print(code)
        if not codeonly(brand):
            pin=input('Enter gc pin: ')
        gccompile()
        print('\n'+str(len(gcdata))+' card entered!')

print('\n')    
for l in gcprint:
    print(l)
with open(directory, 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(gcdata)

#process()