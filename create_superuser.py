from apps.users.utils import Users
from apps.users.models.requests import UserCreate, RoleOptions
from config import settings
from database.connection import Session, engine

def create_user(username, password, session):
    user = Users.create_user(
        user_data = UserCreate(
            username = username,
            password = password,
        ),
        role = RoleOptions.admin,
        db = session)
    return user

username = input('username: ')
password = input('password: ')

with Session(engine) as session:
    create_user(username, password, session)