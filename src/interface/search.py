from src.core.entity.point_of_interest_entity import PointOfInterestEntity
from src.core.usecase.point_of_interest_usecase import get_query

class Search():
    def __init__(self, latitude, longitude, kinds, limit,radius):
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.kinds = kinds
        self.limit = int(limit)
        self.radius = float(radius)
    
    def launch(self):
        return get_query([self.latitude, self.longitude],self.kinds,self.limit,self.radius)

