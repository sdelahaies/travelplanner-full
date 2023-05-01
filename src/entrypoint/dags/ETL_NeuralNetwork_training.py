from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python import PythonOperator

from datetime import datetime

from pymongo import MongoClient
import os

import torch
import torch.nn as nn
import torch.nn.functional as F
import random
import numpy as np
import pandas as pd
#from torch.utils.tensorboard import SummaryWriter

#########################################################
def users_to_ratings():
    URL = os.getenv("MONGODB_URL")
    client = MongoClient(URL)
    testing = client["testing"]
    users =testing.users

    history = list(users.find({},{"_id":1,'history':1}))
    
    users_list=[]
    items_list=[]
    rtngs_list=[]
    for u in history:
        his = u["history"]
        us_list = [str(u["_id"])]*len(his)
        
        it_list = []
        ra_list = []
        for h in his:
            it_list.append(h[0]) 
            ra_list.append(h[1])  
        users_list += us_list 
        items_list += it_list     
        rtngs_list += ra_list
        

    df = pd.DataFrame([users_list,items_list,rtngs_list]).transpose()
    df.columns = (["userId","itemId","rating"])
    df.to_csv("datalake/ratings.csv",index=False)

#########################################################



def set_device():
  return "cuda" if torch.cuda.is_available() else "cpu"

def set_seed(seed=None, seed_torch=True):
  if seed is None:
    seed = np.random.choice(2 ** 32)
  random.seed(seed)
  np.random.seed(seed)
  if seed_torch:
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
  print(f'Random seed {seed} has been set.')
  

def proc_col(col, train_col=None):
    """Encodes a pandas column with continous ids. 
    """
    uniq = train_col.unique() if train_col is not None else col.unique()
    name2idx = {o:i for i,o in enumerate(uniq)}
    return name2idx, np.array([name2idx.get(x, -1) for x in col]), len(uniq)

def encode_data(df, train=None):
    """ Encodes rating data with continous user and movie ids. 
    If train is provided, encodes df with the same encoding as train.
    """
    df = df.copy()
    for col_name in ["userId", "itemId"]:
        train_col = None
        if train is not None:
            train_col = train[col_name]
        _,col,_ = proc_col(df[col_name], train_col)
        df[col_name+"_original"]=df[col_name]
        df[col_name] = col
        df = df[df[col_name] >= 0]
    return df

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

def train_epochs(df_train, df_val, DEVICE, model, epochs=10, lr=0.01, wd=0.0, unsqueeze=False):
    loss_list=[]
    loss_val_list=[]
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=wd)
    
    users = torch.LongTensor(df_train.userId.values).to(DEVICE)
    items = torch.LongTensor(df_train.itemId.values).to(DEVICE)
    ratings = torch.FloatTensor(df_train.rating.values).to(DEVICE)
    if unsqueeze:
        ratings = ratings.unsqueeze(1)
    
    users_val = torch.LongTensor(df_val.userId.values).to(DEVICE)
    items_val = torch.LongTensor(df_val.itemId.values).to(DEVICE)
    ratings_val = torch.FloatTensor(df_val.rating.values).to(DEVICE)
    if unsqueeze:
        ratings_val = ratings_val.unsqueeze(1)
     
    for i in range(epochs):
        model.train()
        y_hat = model(users, items)
        loss = F.mse_loss(y_hat, ratings)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        loss_list.append(loss.item())
        #writer.add_scalar('loss',loss,i)
        
        if i % 10 ==0:  # compute validation loss
            model.eval()
            y_hat = model(users_val, items_val)
            loss_val = F.mse_loss(y_hat, ratings_val)
            #writer.add_scalar('loss_val',loss_val,i)
            loss_val_list.append(loss_val.item())
            print(i,loss.item(),loss_val.item())
        else:
            print(i,loss.item())
    
    return loss_list,loss_val_list

my_dag = DAG(
    dag_id='ETL_NeuralNetwork_training',
    tags=['ETL','NeuralNetwork','training'],
    schedule_interval=None,
    default_args={
        'owner': 'airflow',
        'start_date': datetime(2022, 5, 28)
    },
    catchup=False
)


def ETL_get_data():
    return users_to_ratings()

def train_NeuralNetwork(filename):
    
    SEED = 42                  # put SEED in conf file
    set_seed(seed=SEED)
    DEVICE = set_device()
    
    
    data = pd.read_csv(filename)
    # split train and validation before encoding
    msk = np.random.rand(len(data)) < 0.8
    train = data[msk].copy()
    val = data[~msk].copy()
        
    df_train = encode_data(train)
    df_val = encode_data(val, train)
    df_train.to_csv('datalake/model/ratings_emb.csv',index=False)
    
    n_users = len(df_train.userId.unique())
    n_items = len(df_train.itemId.unique())
    print(n_users, n_items) 

    model = CFNet(n_users, n_items, emb_size=100,n_hidden=20).to(DEVICE)

    print(model)
    #writer = SummaryWriter()
    #writer.add_graph(model,
    #                [torch.LongTensor(df_val.userId.values).to(DEVICE),
    #                torch.LongTensor(df_val.itemId.values).to(DEVICE)
    #            ])     
    
    loss_list,loss_val_list = train_epochs(df_train, df_val, DEVICE,model, epochs=200, lr=0.01, wd=1e-6, unsqueeze=True)
    
    torch.save(model.state_dict(), "datalake/model/NCFNet_emb100_hid20.pt")
    
    return print(DEVICE)

getData = PythonOperator(
    task_id='ETL_get_data',
    python_callable=ETL_get_data,
    dag=my_dag
)

trainModel = PythonOperator(
    task_id='train_NeuralNetwork',
    python_callable=train_NeuralNetwork,
    dag=my_dag,
    op_kwargs= {
        'filename': 'datalake/ratings.csv'
    }
)

getData >> trainModel