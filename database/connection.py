from typing import Annotated

from fastapi import Depends
from sqlmodel import create_engine, SQLModel, Session
from config import settings

dbconnector = settings.database.CONNECTOR
dbhost = settings.database.HOST
dbport = settings.database.PORT
dbname = settings.database.DB_NAME
dbuser = settings.database.DB_USER
dbpassword = settings.database.DB_PASSWORD

dbfullhost = str(dbhost) + ":" + str(dbport) + '/' + str(dbname)

url = str(dbconnector) + "://" + str(dbuser) + ":" + str(dbpassword) + "@" + str(dbfullhost)
    
engine = create_engine(url, echo=settings.DEBUG)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

DBSessionDep = Annotated[Session, Depends(get_session)]

# from sqlmodel import create_engine, SQLModel, Session
# from config import settings

# class DatabaseEngine():
    
#     # singleton
#     _instance = None
#     def __new__(cls):
#         if cls._instance is None:
#             cls._instance = super(DatabaseEngine, cls).__new__(cls)
#         return cls._instance

#     dbconnector = settings.database.CONNECTOR
#     dbhost = settings.database.HOST
#     dbport = settings.database.PORT
#     dbname = settings.database.DB_NAME
#     dbuser = settings.database.DB_USER
#     dbpassword = settings.database.DB_PASSWORD
    
#     dbfullhost = str(dbhost) + ":" + str(dbport) + '/' + str(dbname)
    
#     url = str(dbconnector) + "://" + str(dbuser) + ":" + str(dbpassword) + "@" + str(dbfullhost) + "?charset=utf8mb4"
        
#     engine = create_engine(url, echo=settings.DEBUG)

#     def init_db(self):
#         SQLModel.metadata.create_all(self.engine)

#     def get_session(self):
#         with Session(self.engine) as session:
#             yield session

# db_engine = DatabaseEngine()