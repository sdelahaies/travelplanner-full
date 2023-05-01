"""
   DAG to delete the DB DTourism and POI collection
"""

from airflow import DAG
from airflow.decorators import task
from airflow.operators.empty import EmptyOperator
from src.interface.importer import Importer

from pymongo import MongoClient
import json
import os
from datetime import datetime

with DAG(dag_id='delete_databases',
         start_date=datetime(2022, 5, 28),
         tags = ['database'],
         schedule_interval=None) as dag:

    dag.doc_md = __doc__    
    

    @task.branch(task_id="delete_databases")
    def delete_databases():
        
        URL = os.getenv("MONGODB_URL")
        DB = os.getenv("MONGODB_DB")

        client = MongoClient(URL)
        
        itinerary = client["itinerary"]
        itinerary.point_of_interest.drop()
        itinerary.user.drop()
        client.drop_database("itinerary")
        
        testing = client["testing"]
        testing.users.drop()
        client.drop_database("testing")
        
        
        return(print("all Databases deleted"))
    
    deleteDatabases = delete_databases()

    

deleteDatabases    


