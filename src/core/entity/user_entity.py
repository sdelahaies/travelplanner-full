from flask_bcrypt import generate_password_hash, check_password_hash

"""
This user entity
"""

class UserEntity:
    """
    This is a class for defined user

    Parameters:
        username (string): the username
        password (string): the password
    """

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.password_hash = None

    def verify_password(self, password):
        return check_password_hash(self.password, password)
    
    def generate_password(self):
        self.password_hash = generate_password_hash(self.password, 10)
    
    def getDict(self):
        return {
            "username": self.username,
            "password": self.password,
            "password_hash": self.password_hash
        }
