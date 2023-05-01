"""
   DAG to get reviews from tripadvisor
   
   takes the activities' url scraped with
   the dag scraping_tripadvisor_activities_dpt.py
   and scrap reviews 
"""

from airflow import DAG
from airflow.decorators import task
from airflow.operators.empty import EmptyOperator

import pandas as pd
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from time import sleep
from datetime import datetime
import warnings
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
warnings.filterwarnings("ignore")
import contextlib

def get_dpt():
    df = pd.read_csv('datalake/dpt.csv',index_col=0)
    sample = df[(df.scraped == 1) & (df.reviews == 0)].sample(n=1)
    nom = sample.nom_cap.iloc[0]
    no = str(sample.index.to_list()[0])
    return nom, no

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

def get_review(driver,t):
    review = init_review()
    AA = t.find_elements(By.CSS_SELECTOR,"*")
    cleaned_text = t.text.replace("Cet avis est l'opinion subjective d'un membre de Tripadvisor et non l'avis de Tripadvisor LLC. Les avis sont soumis à des vérifications de la part de Tripadvisor."," ")
    cleaned_text = cleaned_text.replace("Cette réponse est l'opinion subjective du gérant et non de Tripadvisor LLC."," OWNER ")
    
    review["raw"]=cleaned_text
    for a in AA:
        attributes=driver.execute_script('var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;', a)
        if 'aria-hidden' in attributes:
            review["username"]=attributes['href'].replace('/Profile/','')
        if ('aria-label' in attributes) & ('viewBox' in attributes):
            review["rate"]=attributes['aria-label']
    #reviewsList.append(review)
    #pprint(review)
    return review

def init_review():
    return {
        "username": 'NA',
        "raw": 'NA',
        "rate": 'NA',
    }


with DAG(dag_id='scraping_tripadvisor_reviews',
         start_date=datetime(2022, 5, 28),
         tags = ['scraping','tripadvisor'],
         schedule_interval=None) as dag:

    dag.doc_md = __doc__    
    
    @task.branch(task_id="scrap-reviews")
    def scrap_reviews():
        
        nom, no = get_dpt()
        finput = f"datalake/scraped/data/dpt/attractions_{no}.json"
        print(nom,no)

        with open(finput, 'r') as f:
            data = json.load(f)

        #init driver
        options = webdriver.FirefoxOptions()
        options.headless = True
        driver = webdriver.Firefox(options=options)
        reviewsDpt=[]
        #for i in range(len(data)):
        for i in range(1):
            if data[i]['url'] != 'NA':
                print(data[i]['name'])
                url0 = "https://tripadvisor.fr"+data[i]['url']

                driver.get(url0)
                print(url0)
                sleep(3)

                if i == 0:
                    RGPD = driver.find_element(By.ID, value="onetrust-reject-all-handler")
                    driver.execute_script("arguments[0].click();", RGPD)

                attraction ={'url':url0}

                try:
                    tmp = driver.find_element(By.CLASS_NAME,"Ci")
                    nb_items_str = tmp.text.split(" ")[-1]
                    nb_items = get_int(nb_items_str)
                    nb_pages = nb_items % 10
                except Exception:
                    nb_pages = 7

                with contextlib.suppress(Exception):
                    reviewsList = []
        #            for i in range(nb_pages):
                    for i in range(1):
                        if i!=0:
                            url = url0.replace("Reviews-", f"Reviews-or{str(i * 10)}")
                            #print(url)
                            driver.get(url)
                            sleep(2)

                        TT=driver.find_elements(By.XPATH,"//div[@data-automation='reviewCard']")

                        for t in TT:
                            review=get_review(driver,t)
                            #pprint(review)
                            reviewsList.append(review)
                attraction['reviews'] = reviewsList

                reviewsDpt.append(attraction)

        reviewsString = json.dumps(reviewsDpt, indent=4, ensure_ascii=False)
        #from datetime import datetime
        #now = datetime.now()
        #date_time = now.strftime("%m-%d-%Y_%H-%M-%S")
        fname = f"datalake/scraped/data/reviews/test/reviews_{no}.json"
        with open(fname, "w") as jsonFile:
                    jsonFile.write(reviewsString)

        df = pd.read_csv('datalake/dpt.csv',index_col=0)
        df.at[no,"reviews"]=1
        df.to_csv('datalake/dpt.csv')

        driver.quit()

    
    scrapReviews = scrap_reviews() 

    #end_task = EmptyOperator(task_id='end')
    
scrapReviews
#start_task >> importDTourism
#importDTourism >> end_task
