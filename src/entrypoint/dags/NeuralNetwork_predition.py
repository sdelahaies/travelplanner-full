from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python import PythonOperator

from datetime import datetime

from pymongo import MongoClient
import os
import json
import torch
import torch.nn as nn
import torch.nn.functional as F
import random
import numpy as np
import pandas as pd


def set_device():
  return "cuda" if torch.cuda.is_available() else "cpu"

class CFNet(nn.Module):
    def __init__(self, n_users, n_items, emb_size=100, n_hidden=10):
        super(CFNet, self).__init__()
        self.user_emb = nn.Embedding(n_users, emb_size)
        self.item_emb = nn.Embedding(n_items, emb_size)
        self.lin1 = nn.Linear(emb_size*2, n_hidden)
        self.lin2 = nn.Linear(n_hidden, 1)
        self.drop1 = nn.Dropout(0.1)
        
    def forward(self, u, v):
        U = self.user_emb(u)
        V = self.item_emb(v)
        x = F.relu(torch.cat([U, V], dim=1))
        x = self.drop1(x)
        x = F.relu(self.lin1(x))
        x = self.lin2(x)
        return x
    
    
    

my_dag = DAG(
    dag_id='NeuralNetwork_prediction',
    tags=['NeuralNetwork','prediction'],
    schedule_interval=None,
    default_args={
        'owner': 'airflow',
        'start_date': datetime(2022, 5, 28)
    },
    catchup=False
)



def prepare_input():
    
    df =pd.read_csv("datalake/model/ratings_emb.csv")
    n_users = len(df.userId.unique())
    n_items = len(df.itemId.unique())
    df_sample=df.sample(1)
    userId = df_sample.userId_original.values[0]
    sampleIds = df.itemId_original.drop_duplicates()
    
    itemId = random.choices(sampleIds,k=50)
    user_input={
        'n_users':n_users,
        'n_items':n_items,
        'userId':userId,
        'itemId':itemId  
    }
    with open("datalake/model/user_input.json", "w") as final:
        json.dump(user_input, final,indent=4, sort_keys=True, default=str)
    return "input"

def predict_rating(input_file,input_model):
    DEVICE = set_device()
    
    with open(input_file, 'r', encoding='utf-8') as usersfile:
        inputJson = json.load(usersfile)
    n_users = inputJson["n_users"]
    n_items = inputJson["n_items"]
    userId = inputJson["userId"]
    itemId = inputJson["itemId"]
    
    
    model = CFNet(n_users = n_users,n_items = n_items,emb_size=100,n_hidden=20).to(DEVICE)    
    model.load_state_dict(torch.load(input_model))
    model.eval()
    
    df= pd.read_csv("datalake/model/ratings_emb.csv")
    df_items = df[['itemId','itemId_original']].drop_duplicates()
    df_users = df[['userId','userId_original']].drop_duplicates()
    u_emb = [df_users[df_users.userId_original == userId]["userId"].values[0]]*50
    i_emb = [
        df_items[df_items.itemId_original == i]["itemId"].values[0]
        for i in itemId
        ]
    with torch.no_grad():
        prediction = model(torch.tensor(u_emb).to(DEVICE),torch.tensor(i_emb).to(DEVICE))
    
    pred = prediction.numpy()
    user_prediction={
        'userId':userId,
        'itemId':itemId,  
        'rating':[r for r in pred]  
    }
    with open("datalake/model/user_prediction.json", "w") as final:
        json.dump(user_prediction, final,indent=4, sort_keys=True, default=str)
    return "success"

prepareInput = PythonOperator(
    task_id='prepare_input',
    python_callable=prepare_input,
    dag=my_dag
)

predictRating = PythonOperator(
    task_id='predict_rating',
    python_callable=predict_rating,
    dag=my_dag,
    op_kwargs= {
        'input_file': 'datalake/model/user_input.json',
        'input_model': 'datalake/model/NCFNet_emb100_hid20.pt'
    }
)

prepareInput>>predictRating