#!/usr/bin/env python
# coding: utf-8

# In[1]:


# offer grp: JCfPqpmhXroGe0c94WsDRe, only me grp: DXqnN42tpV27ZoVWszBH9D

# import
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import duckdb
from googleapiclient.discovery import build
from google.oauth2 import service_account
import pywhatkit
import time

# accumulators
start_time = time.time()
df = pd.DataFrame()

# credentials
SERVICE_ACCOUNT_FILE = 'read-write-to-gsheet-apis-1-04f16c652b1e.json'
SAMPLE_SPREADSHEET_ID = '1gkLRp59RyRw4UFds0-nNQhhWOaS4VFxtJ_Hgwg2x2A0'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# API
def sheet_api():
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    return sheet

# preference
options = webdriver.ChromeOptions()
options.add_argument('ignore-certificate-errors')

# open window
driver = webdriver.Chrome(service=Service(), options=options)
driver.maximize_window()

# url
url = 'https://chaldal.com/'
driver.get(url)
    
# login via FB
driver.find_element(By.CLASS_NAME, 'signInBtn').click()
driver.find_element(By.CLASS_NAME, 'facebookLoginButton').click()

# handles
main_page = driver.current_window_handle
login_page = driver.window_handles[1]
driver.switch_to.window(login_page)

# email, password
driver.find_element(By.XPATH, '//*[@id="email"]').send_keys('shithi30@gmail.com')
driver.find_element(By.XPATH, '//*[@id="pass"]').send_keys('Maitra30\n')
time.sleep(15)

# switch
driver.switch_to.window(main_page)

# Banani
driver.find_element(By.CLASS_NAME, 'locationMarkerIcon').click()
elems = driver.find_elements(By.CLASS_NAME, 'area-name')
for elem in elems: 
    if 'Banani' in elem.text:
        elem.click()

# reload
driver.refresh()

# offers
url = 'https://chaldal.com/offers'
driver.get(url)

# soup
soup_init = BeautifulSoup(driver.page_source, 'html.parser')
soup = soup_init.find_all("div", attrs={"class": "imageWrapper"})

# location
loc = driver.find_element(By.CLASS_NAME, "metropolitanAreaName").text.replace("\n", " ")

# close window
driver.close()

# brands
brands = ['Boost Health', 'Boost Drink', 'Boost Jar', 'Clear Shampoo', 'Simple Fac', 'Simple Mask', 'Pepsodent', 'Brylcreem', 'Bru Coffee', 'St. Ives', 'St.Ives', 'Horlicks', 'Sunsilk', 'Sun Silk', 'Lux', 'Ponds', "Pond's", 'Closeup', 'Close Up', 'Cif', 'Dove', 'Maltova', 'Domex', 'Clinic Plus', 'Tresemme', 'Tresemmé', 'GlucoMax', 'Knorr', 'Glow Lovely', 'Fair Lovely', 'Glow Handsome', 'Wheel Wash', 'Axe Body', 'Pureit', 'Lifebuoy', 'Surf Excel', 'Vaseline', 'Vim', 'Rin']

# offers
skus = []
for i in range(0, len(soup)):
    sku = ''
    # name
    try: val = soup[i].find("div", attrs={"class": "name"}).get_text()
    except: val = None
    sku = sku + val
    # quantity
    try: val = soup[i].find("div", attrs={"class": "subText"}).get_text()
    except: val = None
    sku = sku + ' ' + val
    # enlist
    skus.append(str(i+1)+". "+sku)
print(skus)

# Unilever offers
ubl_skus = set()
for s in skus:
    for b in brands:
        bb = b.split()
        if len(bb) == 1: bb.append('')
        if bb[0].lower() + ' ' in s.lower() and bb[1].lower() in s.lower(): ubl_skus.add(s)
ubl_skus = sorted(ubl_skus)

# tabular
df['offer_serial'] = [int(s.split('.')[0]) for s in ubl_skus]
df['ubl_offer_sku'] = [' '.join(s.split()[1:]) for s in ubl_skus]
df['ubl_offers'] = len(ubl_skus)
df['total_offers'] = len(skus)
df['location'] = loc
df['platform'] = 'Chaldal'
df['report_time'] = time.strftime('%d-%b-%y, %I:%M %p')
df = duckdb.query('''select * from df order by offer_serial asc''').df()
display(df)

# call API
sheet = sheet_api()
# extract
values = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range='Offers!A1:G').execute().get('values', [])
df_prev = pd.DataFrame(values[1:] , columns = values[0])
# transform
qry = '''select * from (select * from df_prev union all select * from df) tbl1 order by strptime(report_time, '%d-%b-%y, %I:%M %p') desc'''
df_now = duckdb.query(qry).df().fillna('')
# load
res = sheet.values().clear(spreadsheetId=SAMPLE_SPREADSHEET_ID, range='Offers').execute()
res = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="'Offers'!A1", valueInputOption='USER_ENTERED', body={'values': [df_now.columns.values.tolist()] + df_now.values.tolist()}).execute()

# # send
# emo = ':checkmark\t' if len(ubl_skus)>=10 else ':warning\t'
# msg = emo + " Auto Update: " + str(len(ubl_skus)) + " Unilever offers, among total " + str(len(skus)) + ", are currently running on Chaldal.com.\n" + "\n".join(ubl_skus) + "\n* Location: " + loc
# pywhatkit.sendwhatmsg_to_group_instantly(group_id="DXqnN42tpV27ZoVWszBH9D", message=msg, tab_close=True)

# stats
elapsed_time = time.time() - start_time
print("Elapsed time to report (sec): " + str(round(elapsed_time)))


# In[ ]:




