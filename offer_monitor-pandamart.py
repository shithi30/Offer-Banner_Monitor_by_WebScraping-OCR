#!/usr/bin/env python
# coding: utf-8

# ref: https://www.webnots.com/emoji-shortcuts-for-whatsapp-web-and-desktop/
# offer group: JCfPqpmhXroGe0c94WsDRe, only me group: DXqnN42tpV27ZoVWszBH9D

# import
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import duckdb
import time
import pywhatkit

# open window
driver = webdriver.Chrome('chromedriver', options=[])
driver.maximize_window()

# url
url = 'https://www.foodpanda.com.bd/darkstore/h9jp/pandamart-mirpur/'
driver.get(url)

# cross
time.sleep(4)
elem = driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div/button')
elem.click()
    
# soup
soup_init = BeautifulSoup(driver.page_source, 'html.parser')
soup = soup_init.find_all('a', attrs={'class': 'campaign-banners-swiper-link'})

# accumulators
df_acc = pd.DataFrame()
start_time = time.time()
    
# banners
elems = driver.find_elements(By.CLASS_NAME, 'campaign-banners-swiper-link')
banners = len(elems)
for i in range(0, banners): 
    elems = driver.find_elements(By.CLASS_NAME, 'campaign-banners-swiper-link')
    elem = elems[i]
    ActionChains(driver).move_to_element(elem).click().perform()
    
    # scroll
    last_height = driver.execute_script('return document.body.scrollHeight')
    while True:
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        time.sleep(4)
        new_height = driver.execute_script('return document.body.scrollHeight')
        if new_height == last_height: break
        last_height = new_height
    
    # soup
    soup_init = BeautifulSoup(driver.page_source, 'html.parser')
    soup = soup_init.find_all('div', attrs={'class', 'box-flex product-card-attributes'})

    # scrape
    df = pd.DataFrame()
    df['sku'] = [s.find('p', attrs={'class', 'product-card-name'}).get_text() for s in soup]
    offers = []
    for s in soup:
        try: offers.append(s.find("span", attrs={"class", "bds-c-tag__label"}).get_text())
        except: offers.append(None)
    df['offer'] = offers
    df['banner'] = i+1
    df_acc = df_acc.append(df)
    
    # record
    print(str(df.shape[0]) + ', b-' + str(i+1) + ': ' + driver.current_url)
    sku_count = df_acc.shape[0]
    
    # back
    driver.back()

# close window
driver.close()

# Unilever offers
brands = ['Boost Health', 'Boost Drink', 'Boost Jar', 'Clear Shampoo', 'Simple Fac', 'Simple Mask', 'Pepsodent', 'Brylcreem', 'Bru Coffee', 'St. Ives', 'St.Ives', 'Horlicks', 'Sunsilk', 'Sun Silk', 'Lux', 'Ponds', "Pond's", 'Closeup', 'Close Up', 'Cif', 'Dove', 'Maltova', 'Domex', 'Clinic Plus', 'Tresemme', 'Tresemmé', 'GlucoMax', 'Knorr', 'Glow Lovely', 'Fair Lovely', 'Glow Handsome', 'Wheel Wash', 'Axe Body', 'Pureit', 'Lifebuoy', 'Surf Excel', 'Vaseline', 'Vim', 'Rin']
skus = df_acc['sku'].tolist()
if_ubl = [None]*sku_count
for i in range(0, sku_count):
    for b in brands:
        bb = b.split()
        if len(bb) == 1: bb.append('')
        if bb[0].lower() + ' ' in skus[i].lower() and bb[1].lower() in skus[i].lower(): if_ubl[i] = b
df_acc['brand_if_unilever'] = if_ubl

# save
df_acc.to_csv('pandamart_offers.csv', index=False)

# analysis
qry = '''
select 
    '-> Total banners: ' attr, 
    count(distinct banner) val
from df_acc 

union all

select 
    '-> Unilever banners: ' attr, 
    count(distinct banner) val
from df_acc 
where brand_if_unilever is not null

union all 

select 
    concat('-> Banner-', banner::string, ': ') attr, 
    concat(count(1)::string, ' Unilever SKUs, ', count(case when offer is not null then 1 else null end)::string, ' with ongoing offers') val
from df_acc 
where brand_if_unilever is not null
group by 1

union all

select 
    '* Numeric distribution in banners: ' attr, 
    round(count(distinct case when brand_if_unilever is not null then banner else null end)*1.00/count(distinct banner), 2) val 
from df_acc 

union all

select 
    '* Weighted distribution in banners: ' attr, 
    round(count(case when banner in(select distinct banner from df_acc where brand_if_unilever is not null) then 1 else null end)*1.00/count(1), 2) val 
from df_acc;
'''
res_df = duckdb.query(qry).df()
display(res_df)

# send 
attr_ls = res_df['attr'].tolist()
val_ls = res_df['val'].tolist()
msg = ':sound\t Auto Update: ' + val_ls[1] + ' banners, among total ' + val_ls[0] + ', are displaying Unilever products on Pandamart carousels: '
for i in range(2, len(attr_ls)): msg = msg + '\n' + attr_ls[i] + val_ls[i]
print('\n' + msg)
pywhatkit.sendwhatmsg_to_group_instantly(group_id='JCfPqpmhXroGe0c94WsDRe', message=msg, tab_close=True)

# stats
elapsed_time = time.time() - start_time
print('\nElapsed time to report: ' + str(round(elapsed_time / 60.00, 2)))
