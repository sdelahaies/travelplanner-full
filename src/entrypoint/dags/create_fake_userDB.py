"""
   DAG to generate fake users with history
   and ratings to test model training and
   prediction. 
   
   1. Creates a json.
   2. Load it 
   
"""   

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python import PythonOperator

import json
#import pprint as pprint
import random
import datetime

from pymongo import MongoClient
import os

def get_pois_id():
    URL = os.getenv("MONGODB_URL")
    client = MongoClient(URL)
    itinerary = client["itinerary"]
    pois = itinerary.point_of_interest
    ids = list(pois.find({},{"_id":1}))
    return [str(i["_id"]) for i in ids]
    
def create_fake_users():
    n_items =200000
    itemId = get_pois_id()
    users=[]
    for i in range(50):
        n=random.randint(1,300)
        history = [
            (
                #random.choice(range(n_items)),
                random.choice(itemId),
                5 * random.random(),
                datetime.datetime.now(),
            ) for _ in range(n)
        ]
        user = {
            "username": f"user_{i}",
            "password": "password",
            "history": history
            }
        users.append(user)    

    with open("datalake/users.json", "w") as final:
        json.dump(users, final,indent=4, sort_keys=True, default=str)
    return "success"

def import_fake_users_to_db():
    URL = os.getenv("MONGODB_URL")
    client = MongoClient(URL)
    testing = client["testing"]

    #print(client.list_database_names())
    if 'users' not in testing.list_collection_names():
        testing.create_collection(name='users')
    else:
        testing.users.drop()

    #print(testing.list_collection_names())

    users =testing.users

    with open("datalake/users.json", 'r', encoding='utf-8') as usersfile:
        usersJson = json.load(usersfile)
        for user in usersJson:
            users.insert_one(user)   
            
    return print("number of users: ",users.count_documents({}))


my_dag = DAG(
    dag_id='create_fake_users',
    tags=['testing','users','history'],
    schedule_interval=None,
    default_args={
        'owner': 'airflow',
        'start_date': datetime.datetime(2022, 5, 28)
    },
    catchup=False
)

# getPoisId = PythonOperator(
#     task_id='get-pois-id',
#     python_callable=get_pois_id,
#     dag=my_dag,
# )

createFakeUsers = PythonOperator(
    task_id='create-fake-users',
    python_callable=create_fake_users,
    dag=my_dag,
)

importFakeUsersToDB = PythonOperator(
    task_id='import-fake-users',
    python_callable=import_fake_users_to_db,
    dag=my_dag,
)


createFakeUsers>>importFakeUsersToDB