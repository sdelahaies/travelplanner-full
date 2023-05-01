"""
DAG to scrap tripadvisor's recommended 
activities by department    
"""
from airflow import DAG
from airflow.decorators import task
from airflow.operators.empty import EmptyOperator

import pandas as pd
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from time import sleep
import warnings
#from pprint import pprint
import json
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import logging
import os
warnings.filterwarnings("ignore")

def get_int(int_str):
    spaces = ['\t','\x0b','\x0c','\r','\x1c','\x1d',
              '\x1e','\x1f','\x85','\xa0','\u1680',
              '\u2000','\u2001','\u2002','\u2003','\u2004',
              '\u2005','\u2006','\u2007','\u2008','\u2009',
              '\u200a','\u2028','\u2029','\u202f','\u205f',
              '\u3000']
    for s in spaces:
        int_str = int_str.replace(s,"")
    return int(int_str)

def get_dpt():
    df = pd.read_csv('datalake/dpt.csv',index_col=0)
    #sample = df[df.scraped == 0].sample(n=1)
    sample = df.sample(n=1)
    nom = sample.nom_cap.iloc[0]
    no = str(sample.index.to_list()[0])
    return nom, no

def init_item():
    return {
        "name": 'NA',
        "type": 'NA',
        "votes": 'NA',
        "rate": 'NA',
        "url": 'NA',
    }
    
def get_item(driver,item_elements):
    item=init_item()
    for t in item_elements:
        attributes = driver.execute_script('var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;', t)
        if "name" in attributes:
            item["name"]=t.text
        if "class" in attributes: 
            if attributes["class"] == "BKifx":
                item["type"]=t.text
            if "aria-label" in attributes:
                item["rate"]=attributes["aria-label"]
            if (
                attributes["class"] == "BMQDV _F G- wSSLS SwZTJ FGwzt ukgoS"
            ) & ('href' in attributes) and (
                "Attraction" in attributes['href']
            ) & (
                "ShowUserReviews" not in attributes['href']
            ):
                item["votes"]=t.text
                item["url"]=attributes["href"]
    return item


with DAG(dag_id='scraping_tripadvisor_activities',
         start_date=datetime(2022, 5, 28),
         schedule_interval=None,
         tags = ['scraping','tripadvisor']) as dag:

    dag.doc_md = __doc__    
    
    @task.branch(task_id="scrap-activities")
    def scrap_activities():

        nom, no = get_dpt()

        #init driver
        options = webdriver.FirefoxOptions()
        options.headless = True
        driver = webdriver.Firefox(options=options)

        status = 0
        logging.basicConfig(
            filename=f"datalake/scraped/error_logs/dpt/dag/{no}.log", level=logging.INFO)
        try:
            # google query
            driver.get("https://www.google.fr/")
            gRGPD = driver.find_element(By.ID, value="L2AGLb")
            driver.execute_script("arguments[0].click();", gRGPD)
            google = driver.current_window_handle
            searchbar = driver.find_element(by='name', value='q')
            searchbar.send_keys(f"tripadvisor tourisme {nom} {no}")
            searchbar.send_keys(Keys.ENTER)
            sleep(1)
            link = driver.find_element(by='class name', value='qLRx3b')
            link.click()
            sleep(3)
            #tripadvisor
            RGPD = driver.find_element(By.ID, value="onetrust-reject-all-handler")
            driver.execute_script("arguments[0].click();", RGPD)
            sleep(1)

            elts = driver.find_elements(By.LINK_TEXT, "Tout afficher")
            for e in elts:
                url = e.get_property('href')
                if "Attractions" in e.get_property('href'):
                    url_Attractions = e.get_property('href')
                    #print(url_Attractions)

            driver.get(url_Attractions)
            sleep(1)
            toutAfficher = driver.find_elements(By.LINK_TEXT, "Tout afficher")

            url0 = ''
            for t in toutAfficher:
                attributes = driver.execute_script('var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;', t)
                if "oa0" in attributes['href']:
                    url0 = attributes['href']

            if 'https://www.tripadvisor.fr' not in url0:
                url0 = 'https://www.tripadvisor.fr'+url0


            driver.get(url0)
            sleep(3)

            try:
                tmp = driver.find_element(By.CLASS_NAME,"Ci")
                nb_items_str = tmp.text.split(" ")[-1]
                nb_items = get_int(nb_items_str)
                nb_pages = nb_items % 30
            except Exception:
                nb_pages = 5

            listItems = []
            #for i in range(nb_pages):
            for i in range(1):
                if i!=0:
                    url = url0.replace("oa0", f"oa{str(i * 30)}")
                    driver.get(url)
                    sleep(1)

                items = driver.find_elements(By.CLASS_NAME,"hZuqH")
                for it in items:
                    item = get_item(driver,it.find_elements(By.CSS_SELECTOR,"*"))
                    listItems.append(item)
                    #pprint(item)

            attractionsString = json.dumps(listItems, indent=4, ensure_ascii=False)
            fname = f"datalake/scraped/data/dpt/dag/attractions_{no}.json"
            with open(fname, "w") as jsonFile:
                        jsonFile.write(attractionsString)
            status = 1
            with open("datalake/scraped_dpt.log", "a") as f:
                f.write(f"{no},{nom},1\n")

            df = pd.read_csv('datalake/dpt.csv',index_col=0)
            df.at[no,"scraped"]=1
            df.to_csv('datalake/dpt.csv')

        except Exception as Argument:
            status = 0
            with open("datalake/scraped_dpt.log", "a") as f:
                f.write(f"{no},{nom},0\n")
            logging.exception(str(Argument))


        #if status:
        #    os.remove(f"datalake/scraped/error_logs/dpt/dag/{no}.log")

        driver.quit()
        
    scrapActivities = scrap_activities()

scrapActivities