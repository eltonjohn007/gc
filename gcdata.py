import requests
from bs4 import BeautifulSoup
import re
import csv
import datetime
import time
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import os

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

def pinprocessing(x,y,z):
    if not pd.isna(df[x]['pin']):
        digits=df[x]['pin']
        if digits[-1]=='e':
            z.append(y[-int(digits[:-1]):])
        elif digits[-1]=='f':
            z.append(y[0:int(digits[:-1])])
    return z


def codeonly(x):
    return not pd.isna(df[x]['codeonly'])

def savedir():
#    return 'D:\\Documents\\'+datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")+'.pdf'
    return '../../'+datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")+'.pdf'

#compile gcdata into desired format for output and storage

def click(button):
    clicked=False
    while not clicked:
        try:
            button.click()
            clicked=True
        except:
            button.send_keys(Keys.TAB)
            
def gccompile():
    if gcformat=='1':
            gcdata.append([datetime.datetime.now().strftime("%Y-%m-%d"),source,brand,balance,'\''+code.replace(' ',''),'\''+pin.replace(' ','')])
            gcprint.append(balance+','+code+','+pin)

    elif gcformat=='2':
            gcdata.append([datetime.datetime.now().strftime("%Y-%m-%d"),source,brand,balance,'\''+code.replace(' ',''),'\''+pin.replace(' ','')])
            gcprint.append(code+','+pin+','+balance)

def urlgc(pagesave,url):
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
            driver=webdriver.Chrome(ChromeDriverManager().install())
            driver.minimize_window()
            driver.get(url)
            button=driver.find_element_by_xpath('//*[@ data-nemo="skipbutton"]')
            click(button)
            time.sleep(1)
            text=BeautifulSoup(driver.page_source,'html.parser').text
            driver.close()
        balance=[]
        if re.findall('\"itemValue\":\"(.+?)\"',text)!=[]:
            balance.append(re.findall('\"itemValue\":\"(.+?)\"',text)[0][1:])
        if re.findall('Card(.+?)Card',text)!=[]:
            balance.append(re.findall('Card(.+?)Card',text)[0][1:])
        if len(balance)>0:
            balance=min(balance,key=len)
        else:
            raise ValueError("Format not supported")
        code=[]
        if brand=='wayfair':
            if re.findall('\"security_code\":\"(.+?)\"',text)!=[]:
                code.append(re.findall('\"security_code\":\"(.+?)\"',text)[0])
        else:
            if re.findall('\"card_number\":\"(.+?)\"',text)!=[]:
                code.append(re.findall('\"card_number\":\"(.+?)\"',text)[0])
            if re.findall('Card number(.+?)PIN',text)!=[]:
                code.append(re.findall('Card number(.+?)PIN',text)[0])
        if len(code)>0:
            code=min(code,key=len)
        else:
            raise ValueError("Format not supported")  
        code=brandprocessing(brand,code)
        if not codeonly(brand):
            pin=[]
            if re.findall('\"security_code\":\"(.+?)\"',text)!=[]:
                pin.append(re.findall('\"security_code\":\"(.+?)\"',text)[0])
            if re.findall('PIN(.+?)Scan',text)!=[]:
                pin.append(re.findall('PIN(.+?)Scan',text)[0])
            if len(pin)>0:
                pin=min(pin,key=len)
            else:
                raise ValueError("Format not supported")
    elif 'activationspot' in url or 'blackhawknetwork' in url:
        if pagesave:
            pdfkit.from_url(url,savedir(),configuration=config,options=options)
        text=soup.find('body').text
        if 'Javascript' in text:
            driver=webdriver.Chrome(ChromeDriverManager().install())
            driver.minimize_window()
            driver.get(url)
            try:
                element_present = EC.presence_of_element_located((By.ID, 'main'))
                WebDriverWait(browser, 30).until(element_present)
            except TimeoutException:
                print("Timed out waiting for page to load")
            text=driver.find_element_by_id(id_='main').text
            driver.quit()
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
        if re.findall('CARD\$(.+?)CARD:',text)!=[]:
            balance.append(re.findall('CARD\$(.+?)CARD:',text)[0])
        if re.findall('AMOUNT\:\$(.+?)E-GIFT',text)!=[]:
            balance.append(re.findall('AMOUNT\:\$(.+?)E-GIFT',text)[0])
        if re.findall('CARD\$(.+?)FROM',text)!=[]:
            balance.append(re.findall('CARD\$(.+?)FROM',text)[0])
        if re.findall('YOUR\$(.+?)EGIFT',text)!=[]:
            balance.append(re.findall('YOUR\$(.+?)EGIFT',text)[0])
        if len(balance)>0:
            balance=min(balance,key=len)
        else:
            raise ValueError("Format not supported")
        balance=balance.replace('$','')
        balance=str(int(float(balance)/5)*5)
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
        if re.findall('CARDNUMBER:(.+?)BARCODE',text)!=[]:
            code.append(re.findall('CARDNUMBER:(.+?)BARCODE',text)[0])
        if re.findall('CODE:(.+?)CARD',text)!=[]:
            code.append(re.findall('CODE:(.+?)CARD',text)[0])
        if re.findall('CODE:(.+?)TO',text)!=[]:
            code.append(re.findall('CODE:(.+?)TO',text)[0])
        if re.findall('USDEGIFTCARD(.+?)PIN',text)!=[]:
            code.append(re.findall('USDEGIFTCARD(.+?)PIN',text)[0])
        if len(code)>0:
            code=min(code,key=len)
        else:
            raise ValueError("Format not supported")     
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
            if re.findall('PIN:(.+?)USING',text)!=[]:
                pin.append(re.findall('PIN:(.+?)USING',text)[0])
            if re.findall('PIN:(.+?)BARCODE',text)!=[]:
                pin.append(re.findall('PIN:(.+?)BARCODE',text)[0])
            if re.findall('PIN:(.+?)VALID',text)!=[]:
                pin.append(re.findall('PIN:(.+?)VALID',text)[0])
            pin=pinprocessing(brand,code,pin)
            if len(pin)>0:
                pin=min(pin,key=len)
            else:
                raise ValueError("Format not supported")
        code=brandprocessing(brand,code)
    elif 'vcdelivery' in url:
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
        balance=[]
        if re.findall('YOUR\$(.+?)E-GIFT',text)!=[]:
            balance.append(re.findall('YOUR\$(.+?)E-GIFT',text)[0])
        if re.findall('CARD\$(.+?)USD',text)!=[]:
            balance.append(re.findall('CARD\$(.+?)USD',text)[0])
        if re.findall('YOUR\$(.+?)BONUS',text)!=[]:
            balance.append(re.findall('YOUR\$(.+?)BONUS',text)[0])
        if len(balance)>0:
            balance=min(balance,key=len)
        else:
            raise ValueError("Format not supported")
        balance=balance.replace('$','')
        balance=str(int(float(balance)/5)*5)
        code=[]
        if re.findall('CARDNUMBER:(.+?)PIN',text)!=[]:
            code.append(re.findall('CARDNUMBER:(.+?)PIN',text)[0])
        if re.findall('CARDNUMBER(.+?)COPIED',text)!=[]:
            code.append(re.findall('CARDNUMBER(.+?)COPIED',text)[0])
        if len(code)>0:
            code=min(code,key=len)
            code=brandprocessing(brand,code)
        else:
            raise ValueError("Format not supported")  
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
    return balance,code,pin


def numonly(A):
    B=[l for l in A if l.isdigit() or l.isalpha()]
    return ''.join(B)
#gc directory
#directory='D:\\Documents\\finance\\gift cards\\gcdata.csv'
directory='../../finance/gift cards/gcdata.csv'
#def process():
gcinput=input('Enter input format (1 for url, 2 for gc codes, 3 for scanned codes 1, 4 for scanned codes 2, 5 for excel codes) [Default '+str(df_default['gcinput'].values[0])+']: ')
while gcinput not in {'1','2','3','4','5',''}:
    print('\nWrong format!')
    gcinput=input('Enter input format (1 for url, 2 for gc codes, 3 for scanned codes, 4 for excel codes) [Default '+str(df_default['gcinput'].values[0])+']: ')
if gcinput=='':
    gcinput=str(df_default['gcinput'].values[0])
    
gcformat=input('Enter format (1 for gcw, 2 for tcb) [Default '+str(df_default['gcformat'].values[0])+']: ')
while gcformat not in {'1','2',''}:
    print('\nWrong format!')
    gcformat=input('Enter format: ')
if gcformat=='':
    gcformat=str(df_default['gcformat'].values[0])
        
source=input('\nEnter source [Default '+df_default['source'].values[0]+']: ')
if source=='':
    source=df_default['source'].values[0]
while not ss.contain(source):
    possiblesource=[l for l in ss.sourcelist() if l[0]==source[0]]
    print(possiblesource)
    print('Possible sources. Did you enter wrongly?')
    source=input('Enter source: ')
            
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
gcdata=[]
gcprint=[]
#for url gc parsing
if gcinput=='1':
    if gcformat=='1':
        pagesave=not pd.isna(df[brand]['gcwpdf'])
    if gcformat=='2':
        pagesave=not pd.isna(df[brand]['tcbpdf'])  
    if os.path.isfile('url.csv'):
        urlset=set(pd.read_csv('url.csv')['url'].values)
        for url in urlset:
            (balance,code,pin)=urlgc(pagesave,url)
            gccompile()
            print('\n'+str(len(gcdata))+' card entered!')
    else:
        urlset=set()
    truth=True
    while truth:
        url=input('Enter url:')
        if url=='':
            truth=False
        else:
            try:
                url=requests.get(url).url
                if url in urlset:
                    print('\nDuplicate url!')
                else:
                    urlset.add(url)
                    (balance,code,pin)=urlgc(pagesave,url)
                    gccompile()
                    print('\n'+str(len(gcdata))+' card entered!')
            except:
                df_url=pd.DataFrame(list(urlset),columns=['url'])
                df_url.to_csv('url.csv',index=False)
                raise ValueError("Loading Time Out")
                
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
                pin=numonly(pin)
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
    balance=input('Enter gc balance: ')
    data=input('Enter gc data: ')
    today=datetime.date.today().strftime("%Y")
    gccodes=[x.replace(' ','') for x in data.split('\n') if not 'AM' in x and not 'PM' in x and x!='']    
    for l in range(0,len(gccodes),2):
        code=brandprocessing(brand,gccodes[l])
        pin=gccodes[l+1]
        gccompile()
        print('\n'+str(len(gcdata))+' card entered!')
elif gcinput=='5':
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
if os.path.isfile('url.csv'):
    os.remove('url.csv')
#process()