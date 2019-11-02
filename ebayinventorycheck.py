# -*- coding: utf-8 -*-
"""
Created on Tue Jan  1 22:51:05 2019

@author: elton
"""

import requests
from bs4 import BeautifulSoup
import re
while True:
    url=input('Enter url:')
    page=requests.get(url)
    soup=BeautifulSoup(page.text,'html.parser')
    text = soup.text
    print('\n')
    print('Total Quantity:',re.findall('totalQty\"\:(.+?)\,',text)[0])
    print('Quantity remain:',re.findall('remainQty\"\:(.+?)\,',text)[0])
    print('Limit per buyer:',re.findall('maxQtyPerBuyer\"\:(.+?)\,',text)[0])
