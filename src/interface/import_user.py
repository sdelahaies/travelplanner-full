from .user import User

class ImportUser():
    def __init__(self):
        pass

    def import_entity(self):
        users = [
            dict(username="sylvain", password="password"),
            dict(username="imad", password="password"),
            dict(username="halimo", password="password"),
            dict(username="adrien", password="password"),
            dict(username="travel", password="planner")
            ,
        ]

        for item in users:
            user = User(username=item.get("username"), password=item.get("password"))
            user.create()