import requests
from bs4 import BeautifulSoup
import re
import csv
import datetime
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

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
df_default=pd.read_csv('data/default.csv')

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
            gcdata.append([datetime.datetime.now().strftime("%Y-%m-%d"),source,brand,balance,'\''+code,'\''+pin])
            gcprint.append(balance+','+code+','+pin)

    elif gcformat=='2':
            gcdata.append([datetime.datetime.now().strftime("%Y-%m-%d"),source,brand,balance,'\''+code,'\''+pin])
            gcprint.append(code+','+pin+','+balance)


def numonly(A):
    B=[l for l in A if l.isdigit() or l.isalpha()]
    return ''.join(B)
#gc directory
directory='D:\\Dropbox (MIT)\\Documents\\finance\\gift cards\\gcdata.csv'
#def process():
if 'gcinput' not in locals():
    gcinput=input('Enter input format (1 for url, 2 for gc codes, 3 for scanned codes, 4 for excel codes) [Default '+str(df_default['gcinput'].values[0])+']: ')
    while gcinput not in {'1','2','3','4',''}:
        print('\nWrong format!')
        gcinput=input('Enter input format (1 for url, 2 for gc codes, 3 for scanned codes, 4 for excel codes) [Default '+str(df_default['gcinput'].values[0])+']: ')
    if gcinput=='':
        gcinput=str(df_default['gcinput'].values[0])
    
if 'gcformat' not in locals():
    gcformat=input('Enter format (1 for gcw, 2 for tcb) [Default '+str(df_default['gcformat'].values[0])+']: ')
    while gcformat not in {'1','2',''}:
        print('\nWrong format!')
        gcformat=input('Enter format: ')
    if gcformat=='':
        gcformat=str(df_default['gcformat'].values[0])
        
if 'source' not in locals():
    source=input('\nEnter source [Default '+df_default['source'].values[0]+']: ')
    if source=='':
        source=df_default['source'].values[0]
    while not ss.contain(source):
        possiblesource=[l for l in ss.sourcelist() if l[0]==source[0]]
        print(possiblesource)
        print('Possible sources. Did you enter wrongly?')
        source=input('Enter source: ')
            
if 'brand' not in locals():
    brand=input('\nEnter brand [Default '+df_default['brand'].values[0]+']: ')
    if brand=='':
        brand=df_default['brand'].values[0]
    while not bb.contain(brand):
        possiblebrand=[l for l in bb.brandlist() if l[0]==brand[0]]
        print(possiblebrand)
        print('Possible brands. Did you enter wrongly?')
        brand=input('Enter brand: ') 
df_default=pd.DataFrame({'gcinput':gcinput,'gcformat':gcformat,'source':source,'brand':brand},index=[0])
df_default.to_csv('data/default.csv',index=False)
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
            pin=''
            if 'paypal' in url:
                if pagesave:
                    try:
                        pdfkit.from_string(page.text,savedir(),configuration=config,options=options)
                    except:
                        pass
                text=soup.find('body').text
                if 'javascript' in text.lower():
                    text=str(page.content)
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
                if 'Javascript' in text:
                    option = webdriver.ChromeOptions()
                    option.add_argument("— incognito")
                    browser = webdriver.Chrome(options=option)
                    browser.get(url)
                    browser.minimize_window()
                    try:
                        element_present = EC.presence_of_element_located((By.ID, 'main'))
                        WebDriverWait(browser, 30).until(element_present)
                    except TimeoutException:
                        print("Timed out waiting for page to load")
                    text=browser.find_element_by_id(id_='main').text
                    browser.quit()
                text=text.replace('\xa0','')
                text=text.replace('\n','')
                text=text.replace('\t','')
                text=text.replace('#','')
                text=text.replace(' ','')
                text=text.upper()
                balance=[]
                if re.findall('YOUR\$(.+?)USD',text)!=[]:
                    balance.append(re.findall('YOUR\$(.+?)USD',text)[0])
                if re.findall('VALUE:(.+?)CARD',text)!=[]:
                    balance.append(re.findall('VALUE:(.+?)CARD',text)[0])
                if re.findall('CARD(.+?)TO:',text)!=[]:
                    balance.append(re.findall('CARD(.+?)TO:',text)[0])
                if re.findall('CARD\$(.+?)BARCODE',text)!=[]:
                    balance.append(re.findall('CARD\$(.+?)BARCODE',text)[0])
                if re.findall('\$(.+?)TO',text)!=[]:
                    balance.append(re.findall('\$(.+?)TO',text)[0])
                if re.findall('AMOUNT:(.+?)CARDNUMBER',text)!=[]:
                    balance.append(re.findall('AMOUNT:(.+?)CARDNUMBER',text)[0])
                if re.findall('YOUR\$(.+?)APPLE',text)!=[]:
                    balance.append(re.findall('YOUR\$(.+?)APPLE',text)[0])
                if len(balance)>0:
                    balance=min(balance,key=len)
                else:
                    raise ValueError("Format not supported")
                if not balance.isdigit():
                    balance=''.join([l for l in balance if l.isdigit()])
                code=[]
                if re.findall('CARD:(.+?)PIN',text)!=[]:
                    code.append(re.findall('CARD:(.+?)PIN',text)[0])
                if re.findall('CARDNUMBER:(.+?)SECURITYCODE',text)!=[]:
                    code.append(re.findall('CARDNUMBER:(.+?)SECURITYCODE',text)[0])
                if re.findall('CODE:(.+?)SERIAL',text)!=[]:
                    code.append(re.findall('CODE:(.+?)SERIAL',text)[0])
                if re.findall('CODE:(.+?)CLICK',text)!=[]:
                    code.append(re.findall('CODE:(.+?)CLICK',text)[0])
                if re.findall('CARDNUMBER:(.+?)PIN',text)!=[]:
                    code.append(re.findall('CARDNUMBER:(.+?)PIN',text)[0])
                if re.findall('CARD:(.+?)THE',text)!=[]:
                    code.append(re.findall('CARD:(.+?)THE',text)[0])
                if re.findall('CARD:(.+?)REDEEM',text)!=[]:
                    code.append(re.findall('CARD:(.+?)REDEEM',text)[0])
                if len(code)>0:
                    code=min(code,key=len)
                else:
                    raise ValueError("Format not  supported")     
                if not codeonly(brand):
                    pin=[]
                    if re.findall('PIN:(.+?)TO',text)!=[]:
                        pin.append(re.findall('PIN:(.+?)TO',text)[0])
                    if re.findall('PIN\):(.+?)USING',text)!=[]:
                        pin.append(re.findall('PIN\):(.+?)USING',text)[0])
                    if re.findall('SERIALNUMBER:(.+?)REDEEM',text)!=[]:
                        pin.append(re.findall('SERIALNUMBER:(.+?)REDEEM',text)[0])
                    if re.findall('PIN:(.+?)REDEEM',text)!=[]:
                        pin.append(re.findall('PIN:(.+?)REDEEM',text)[0])
                    if re.findall('PIN:(.+?)BARCODE',text)!=[]:
                        pin.append(re.findall('PIN:(.+?)BARCODE',text)[0])
                    if len(pin)>0:
                        pin=min(pin,key=len)
                    else:
                        raise ValueError("Format not supported")
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
                text=text.replace('\xa0','')
                text=text.replace('\n','')
                text=text.replace('\t','')
                text=text.replace('#','')
                text=text.replace(' ','')
                text=text.upper()
                if re.findall('YOUR\$(.+?)E-GIFT',text)!=[]:
                    balance=str(round(float(re.findall('YOUR\$(.+?)E-GIFT',text)[0])))
                elif re.findall('CARD\$(.+?)USD',text)!=[]:
                    balance=str(round(float(re.findall('CARD\$(.+?)USD',text)[0])))
                else:
                    raise ValueError("Format not supported")
                if re.findall('CARDNUMBER:(.+?)PIN',text)!=[]:
                    code=re.findall('CARDNUMBER:(.+?)PIN',text)[0]
                elif re.findall('CARDNUMBER(.+?)COPIED',text)!=[]:
                    code=re.findall('CARDNUMBER(.+?)COPIED',text)[0]
                else:
                    raise ValueError("Format not supported")
                code=brandprocessing(brand,code)
                if not codeonly(brand):
                    pin=[]
                    if re.findall('PIN:(.+?)SEND',text)!=[]:
                        pin.append(re.findall('PIN:(.+?)SEND',text)[0])
                    if re.findall('PIN(.+?)COPIED',text)!=[]:
                        pin.append(re.findall('PIN(.+?)COPIED',text)[0])
                    if re.findall('PIN:(.+?)USING',text)!=[]:
                        pin.append(re.findall('PIN:(.+?)USING',text)[0])
                    if len(pin)>0:
                        pin=min(pin,key=len)
                    else:
                        raise ValueError("Format not supported")
            elif 'buyatab' in url:
                if pagesave:
                    pdfkit.from_url(url,savedir(),configuration=config,options=options)
                text=str(page.content)
                balance=re.findall('"amount": (.+?),',text)[0][:-5]
                code=re.findall('"sCode": \"(.+?)\",',text)[0]
                if not codeonly(brand):
                    pin=re.findall('"pin": \"(.+?)\",',text)[0]
            else:
                raise ValueError("Format not supported")
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
            pin=''
            if brand=='bloomingdale\'s':
                pin=code[-4:]
            code=brandprocessing(brand,code)
            if not codeonly(brand):
                pin=input('Enter gc pin: ')
            gccompile()
        print('\n'+str(len(gcdata))+' card entered!')
#for scanned gc parsing
elif gcinput=='3':
    balance=input('Enter gc balance: ')
    data=input('Enter gc data: ')
    today=datetime.date.today().strftime("%Y")
    gccodes=[x.replace(' ','') for x in re.split('\n|:',data) if not x=='' and not today in x and not 'PIN' in x and len(x)>7]    
    for l in gccodes:
        code=brandprocessing(brand,l)
        pin=''
        if not codeonly(brand):
            print(code)
            pin=input('Enter gc pin: ')
        gccompile()
        print('\n'+str(len(gcdata))+' card entered!')
elif gcinput=='4':
    data=input('Enter gc data: ')
    gccodes=[x.split('\t') for x in data.split('\n')]
    for l in gccodes:
        code=l[0]
        pin=l[1]
        balance=str(int(float(l[2][1:])))
        gccompile()
print('\n')    
for l in gcprint:
    print(l)
with open(directory, 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(gcdata)

#process()