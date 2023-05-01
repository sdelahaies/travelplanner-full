from src.core.entity.point_of_interest_entity import PointOfInterestEntity
from src.core.usecase.point_of_interest_usecase import create_array,create_index
import os
import json

class Importer():
    def __init__(self):
        pass

    def import_entity(self):
        if not os.path.isfile('datalake/index_processed.json'):
                return "can't find datalake/index_processed.json!"
            
        print("loading datalake/index_processed.json into mongo")
        with open('datalake/index_processed.json') as f:
            points_of_interest = json.load(f)
        result = create_array(points_of_interest)
        create_index()
        print(result)
        return result
                