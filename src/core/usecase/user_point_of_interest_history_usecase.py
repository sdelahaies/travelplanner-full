
from src.core.repository import UserPointOfInterestHistoryRepository

def find_by_user_id(user_id):
    user_repo = UserPointOfInterestHistoryRepository()
    response = user_repo.find_by_user_id(user_id)

    return response

def create(user_id, point_of_interest_id, rating):
    user_repo = UserPointOfInterestHistoryRepository()

    response = user_repo.insert_one(dict(user_id= generate_object_id(user_id), point_of_interest_id = generate_object_id(point_of_interest_id), rating = rating))

    return response

def generate_object_id(id):
    user_repo = UserPointOfInterestHistoryRepository()
    return user_repo.create_object_id(id)
