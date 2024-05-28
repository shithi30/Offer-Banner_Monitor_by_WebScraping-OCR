#!/usr/bin/env python
# coding: utf-8

# In[1]:


## import
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import re
from random import shuffle
import time
import pandas as pd
import duckdb
import os
from google.cloud.vision_v1 import Image, types
from google.cloud import vision_v1
import win32com.client


# In[2]:


## scrape

# accumulators
start_time = time.time()
brands = ['Boost Health', 'Boost Drink', 'Boost Jar', 'Clear Shampoo', 'Simple Fac', 'Simple Mask', 'Pepsodent', 'Brylcreem', 'Bru Coffee', 'St Ives', 'Horlicks', 'Sunsilk', 'Lux', 'Pond', "Pond's", 'Closeup', 'Cif', 'Dove', 'Maltova', 'Domex', 'Clinic Plus', 'Tresemm', 'GlucoMax', 'Knorr', 'Glow Lovely', 'Glow Handsome', 'Wheel Wash', 'Axe Body', 'Pureit', 'Lifebuoy', 'Surf Excel', 'Vaseline', 'Vim', 'Rin', 'Unilever', 'Lakm', 'হরলিক্স', 'ইউনিলিভার']
if_unilever = []
texts = []

# preferences
options = webdriver.ChromeOptions()
options.add_argument("ignore-certificate-errors")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
options.add_argument("headless")
service = Service(executable_path = "C:/Users/Shithi.Maitra/Unilever Codes/Scraping Scripts/chromedriver.exe")

# open window
driver = webdriver.Chrome(options = options, service = service)
driver.maximize_window()

# new + active banners
new_banners = []
act_banners = []
banners_old_df = pd.read_csv("banners.csv")
old_banners = banners_old_df['banner_src'].tolist()


# In[3]:


## Pandamart

# url
urls = [
    'https://www.foodpanda.com.bd/darkstore/w2lx/pandamart-gulshan-w2lx',
    'https://www.foodpanda.com.bd/darkstore/h5rj/pandamart-bashundhara',
    'https://www.foodpanda.com.bd/darkstore/ta7z/pandamart-dhanmondi',
    'https://www.foodpanda.com.bd/darkstore/n7ph/pandamart-uttara',
    'https://www.foodpanda.com.bd/darkstore/v1ts/pandamart-mogbazar',
    'https://www.foodpanda.com.bd/darkstore/q4hz/pandamart-sylhet-02',
    'https://www.foodpanda.com.bd/darkstore/a2er/pandamart-khulna',
    'https://www.foodpanda.com.bd/darkstore/w2nv/pandamart-chittagong-1'
]
shuffle(urls)
driver.get(urls[0])

# soup
soup_init = BeautifulSoup(driver.page_source, "html.parser")
soup = soup_init.find_all("img", attrs={"data-testid": "campaign-banners-swiper-groceries-img"})

# banners
for s in soup: 
    b = s["src"]
    act_banners.append(b)
    if b not in old_banners: new_banners.append(b)


# In[4]:


## Daraz

# url
daraz_url = 'https://www.daraz.com.bd'
driver.get(daraz_url)

# carousel
soup = soup_init.find_all("img", attrs={"class": "main-img"})
for s in soup: 
    try: b = s["data-ks-lazyload"]
    except: b = s["src"]
    act_banners.append(b)
    if b not in old_banners: new_banners.append(b)


# In[5]:


## Shajgoj

# url
shaj_url = 'https://shop.shajgoj.com/'
driver.get(shaj_url)

# horizontal
soup_init = BeautifulSoup(driver.page_source, "html.parser")
soup = soup_init.find_all("div", attrs={"class": "wpb_single_image wpb_content_element vc_align_center"})
for s in soup:
    b = s.find("img")["src"]
    act_banners.append(b)
    if b not in old_banners: new_banners.append(b)
    
# carousel
regex = re.compile("slider-3801 slide.*")
soup = soup_init.find_all("img", attrs={"class": regex})
for s in soup: 
    b = s["src"]
    act_banners.append(b)
    if b not in old_banners: new_banners.append(b)

# grid
soup = soup_init.find_all("div", attrs={"class": "vc_row"})
len_soup = len(soup)
for i in range(0, len_soup):
    if soup[i].get_text() not in ('TOP BRANDS & OFFERS', 'DEALS YOU CANNOT MISS') or 'hide-for-now' in soup[i+1]["class"]: continue
    banners = soup[i+1].find_all("img")
    for bnr in banners: 
        b = bnr["src"]
        act_banners.append(b)
        if b not in old_banners: new_banners.append(b)


# In[6]:


## API

# credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'vision-ai-api-demo-52087-6a6a305cb0c0.json'
client = vision_v1.ImageAnnotatorClient()

# type
types = ['.jpg', '.jpeg', '.png', '.gif']
for bnr in new_banners:
    for t in types:
        if t in bnr.lower(): typ = t
        
#     # response
#     try: image = vision_v1.types.Image(source = vision_v1.types.ImageSource(image_uri = bnr.split(typ)[0] + typ))
#     except: continue
#     response = client.text_detection(image = image)

    # response
    image = vision_v1.types.Image(source = vision_v1.types.ImageSource(image_uri = bnr.split(typ)[0] + typ))
    response = client.text_detection(image = image)

    # OCR
    txt = ""
    text_annotations = response.text_annotations
    for text in text_annotations: txt = txt + " " + text.description.upper().replace("\n", " ")
    texts.append(txt)
    
    # Unilever
    if_ubl = 0
    for b in brands:
        bb = b.split()
        if len(bb) == 1: bb.append("")
        if bb[0].upper() + " " in txt and bb[1].upper() in txt: if_ubl = 1
    if_unilever.append(if_ubl)
            
    # show
    print("Banner: " + bnr + "\nText: " + txt + "\nUnilever? " + str(if_ubl) + "\n")


# In[7]:


## store banners
banners_new_df = pd.DataFrame()
banners_new_df['banner_src'] = new_banners
banners_new_df['banner_ubl'] = if_unilever
duckdb.query('''select * from banners_old_df union select * from banners_new_df''').df().to_csv("banners.csv", index = False)


# In[8]:


## to report
if len(new_banners) > 0:
    qry = '''
    select * 
    from 
        (select * from banners_new_df 
        union 
        select * from banners_old_df where if_unilever=1
        ) tbl1
    where banner_src in(''' + ", ".join(["'" + b.replace("'", "''") + "'" for b in act_banners]) + ''')
    '''
    banners_new_df = duckdb.query(qry).df()
    new_banners = banners_new_df['banner_src'].tolist()
    if_unilever = banners_new_df['banner_ubl'].tolist()


# In[9]:


## email

# object
ol = win32com.client.Dispatch("outlook.application")
newmail = ol.CreateItem(0x0)

# report
banner_cnt = len(new_banners)
intro = '''<center>Dear concern,<br><u>Pandamart, Daraz, Shajgoj</u> banners are now brought under Unilever BD's competition surveillance, enabled by AI-based OCR technology. The images presented here are reflections from ''' + time.strftime('%d-%b-%y, %I:%M %p') + '''.<br>'''
# non-UBL 
new_nonubl = ""
for i in range(0, banner_cnt): 
    if if_unilever[i] == 0: new_nonubl = new_nonubl + '''<img src="''' + new_banners[i] + '''" style="border:1px solid black"><br>'''
if len(new_nonubl) > 0: new_nonubl = '''<br>Below are the new, active <b>non-Unilever banners</b> on the platform:<br><br>''' + new_nonubl
# UBL
new_ubl = ""
for i in range(0, banner_cnt): 
    if if_unilever[i] == 1: new_ubl = new_ubl + '''<img src="''' + new_banners[i] + '''" style="border:1px solid black"><br>'''
if len(new_ubl) > 0: new_ubl = '''<br>Against the non-Unilever banners, here are the active <b>banners by Unilever BD</b>:<br><br>''' + new_ubl
# sign
newmail.HTMLbody = intro + new_nonubl + new_ubl + '''<br>More platforms can be brought under this process on demand. This is an auto email via <i>win32com</i>.<br><br>Thanks,<br>Shithi Maitra<br>Asst. Manager, Cust. Service Excellence<br>Unilever BD Ltd.<br><br></center>'''
    
# Teams
newmail.Subject = "New Competition Banners"
newmail.CC = "Eagle Eye - Alerts <93f21d6e.Unilever.onmicrosoft.com@emea.teams.ms>; avra.barua@unilever.com; safa-e.nafee@unilever.com; rafid-al.mahmood@unilever.com; zoya.rashid@unilever.com; samsuddoha.nayeem@unilever.com; sudipta.saha@unilever.com; asif.rezwan@unilever.com; shithi.maitra@unilever.com"
if len(new_banners) > 0: newmail.Send()


# In[10]:


## statistics
print("Total banners: " + str(len(act_banners)))
print("New banners: " + str(len(new_banners)))
print("Elapsed time to report (sec): " + str(round(time.time() - start_time)))
driver.close()


# In[ ]:




