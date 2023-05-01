
from src.core.repository import PointOfInterestRepository

def create_array(array):
    point_of_interest = PointOfInterestRepository()
    return point_of_interest.bulk_insert_one(array)

def create_index():
    point_of_interest = PointOfInterestRepository()
    point_of_interest.create_index('location.coordinates')

def create(data):
    tourist_information_center = PointOfInterestRepository()
    return tourist_information_center.insert_one(data)

def get_query(destination,kinds,limit,radius):
    tourist_information_center = PointOfInterestRepository()
    return tourist_information_center.get_query(destination,kinds,limit,radius)
