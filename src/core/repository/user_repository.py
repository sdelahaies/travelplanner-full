from . import Database

class UserRepository(Database):
    def __init__(self):
        self.entity = "user"

    def find_by_username(self, username):
        result = self.find_one({
            "username": username
        })

        return result
