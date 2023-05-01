
from src.core.repository import UserRepository

def find_by_username(username):
    user_repo = UserRepository()
    response = user_repo.find_by_username(username)

    return response

def create(username, password):
    user_repo = UserRepository()

    response = user_repo.insert_one(dict(username=username, password=password))

    return response
