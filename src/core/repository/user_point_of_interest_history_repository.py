from . import Database

class UserPointOfInterestHistoryRepository(Database):
    def __init__(self):
        self.entity = "user_point_of_interest_history"
    
    def find_by_user_id(self, user_id):
        result = self.aggregate([
            {
                "$match": {
                    "user_id": self.create_object_id(user_id)
                }
            },
            {
                "$lookup": {
                    "from": "point_of_interest",
                    "localField": "point_of_interest_id",
                    "foreignField": "_id",
                    "as": "poi"
                },
            },
            {
                "$unwind": "$poi"
            },
            {
                "$replaceRoot": { "newRoot": "$poi" }
            }
        ])

        return result
