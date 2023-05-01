from src.core.entity.user_entity import UserEntity
from src.core.usecase.user_usecase import find_by_username, create

class User():
    def __init__(self, username, password):
        self.username = username
        self.password = password
    
    def create(self):
        user_entity = UserEntity(self.username, self.password)        
        user_entity.generate_password()

        create(user_entity.getDict()["username"], user_entity.getDict()["password_hash"])

    def find(self):
        user = find_by_username(self.username)
        return user
    
    def verify_password(self):
        user = find_by_username(self.username)

        if user is None:
            return False

        user_entity = UserEntity(user["username"], user["password"])

        return user_entity.verify_password(self.password)
