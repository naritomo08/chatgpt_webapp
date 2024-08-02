# user.py
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

# サンプルユーザーデータ
users = {
    "testuser": User(id=1, username="testuser", password="testpassword")
}

def get_user(username):
    return users.get(username)