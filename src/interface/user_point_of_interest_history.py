from src.core.entity.user_entity import UserEntity
from src.core.usecase.user_point_of_interest_history_usecase import find_by_user_id, create

class UserPointOfInterestHistory():
    def __init__(self, user_id, point_of_interest_id = None, rating = None):
        self.user_id = user_id
        self.point_of_interest_id = point_of_interest_id
        self.rating = rating
    
    def create(self):
        if self.point_of_interest_id is not None and self.rating is not None and self.user_id is not None:
            create(self.user_id, self.point_of_interest_id, self.rating)

    def find_by_user_id(self):
        if self.user_id is not None:
            user = find_by_user_id(self.user_id)
            return user
