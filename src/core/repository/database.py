import datetime
import os
import bson

import pandas as pd
import pymongo


URL = os.getenv("MONGODB_URL")
DB = os.getenv("MONGODB_DB")

client = pymongo.MongoClient(URL)
mongo = client[DB]

class Database:
    def __init__(self):
        self.entity = ""

    def get_db(self):
        return mongo[self.entity]
    
    def create_index(self,field):
        self.get_db().create_index([(field, pymongo.GEOSPHERE)])
        print("geoindex created") 
    
    def create_object_id(self, id):
        return bson.ObjectId(id)

    def find(self, filter = {}):
        print(filter)
        cursor = self.get_db().find(filter)
        df = pd.DataFrame(list(cursor))
        df['_id'] = df['_id'].astype(str)
        return df.to_dict("records")

    def find_one(self, filter = {}):
        cursor = self.get_db().find_one(filter)
        if cursor is not None:
            cursor.update({
                "_id": str(cursor["_id"])
            })
        return cursor

    def insert_one(self, data):
        data.update({"created_at": datetime.datetime.now()})
        data_id = self.get_db().insert_one(data).inserted_id
        data.update({
            "_id": str(data_id)
        })
        return data

    def bulk_insert_one(self, list_elements):
        array = []
        for item in list_elements:
            item.update({"created_at": datetime.datetime.now()})
            array.append(pymongo.InsertOne(item))
        return self.bulk_write(array)
 
    def bulk_write(self, array):
        result = self.get_db().bulk_write(array)
        return result.bulk_api_result

    def aggregate(self, aggregate):
        result = self.get_db().aggregate(aggregate)
        
        df = pd.DataFrame(list(result))
        df['_id'] = df['_id'].astype(str)
        return df.to_dict("records")
