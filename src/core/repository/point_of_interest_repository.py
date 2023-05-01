from . import Database
import os
import pandas as pd


kind = {'restaurants':"Restaurant",
        'randonnées':"Tour",
        'hotels':"Accommodation",
        'sitesculturels':"CulturalSite",
        'événements':"Event"}

class PointOfInterestRepository(Database):
    def __init__(self):
        self.entity = "point_of_interest"
    
    def get_query(self,destination,kinds,limit,radius):
        print(type(radius))
        query = []
        if ("tout" in kinds) or (kinds == []):
            query = list(self.get_db().find({
                "location.coordinates":{
                    "$nearSphere":
                        [float(destination[0]), float(destination[1])], "$maxDistance": radius*1000}
                        }).limit(limit))
        else:
            subquery=[]
            for i in range(len(kinds)):
                subquery = list(self.get_db().find({
                                "$and":[{"type": kind[kinds[i]]},
                                        {"type": {"$ne" :" Restaurant" }},
                                        {"type": {"$ne" :" Accomodation" }},
                                        {"location.coordinates":{
                                            "$nearSphere": [float(destination[0]), float(destination[1])], "$maxDistance": radius*1000
                                            }
                                         }
                                    ]}).limit(limit))
                query += subquery
        df = pd.DataFrame(query)
        df['_id'] = df['_id'].astype(str)
        return df.to_dict("records")


