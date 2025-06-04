from typing import Annotated

from fastapi import Depends
from sqlmodel import create_engine, SQLModel, Session
from sqlalchemy import text
from config import settings
import logging, asyncio

MAX_RETRIES = 10
RETRY_DELAY = 5

db_connector = settings.database.CONNECTOR
db_host = settings.database.HOST
db_port = settings.database.PORT
db_name = settings.database.DB_NAME
db_user = settings.database.DB_USER
db_password = settings.database.DB_PASSWORD

match db_connector:
    case 'mariadb+mariadbconnector':
        db_fullhost = str(db_host) + ":" + str(db_port) + '/' + str(db_name)

        if db_user != '':
            db_fullhost = '@' + db_fullhost

            if db_password != '':
                db_password = ':' + str(db_password)

        full_url = str(db_connector) + "://" + str(db_user) + str(db_password)  + str(db_fullhost)
# Documentação de url de conexão do sqlalchemy:
# https://docs.sqlalchemy.org/en/20/core/engines.html#backend-specific-urls
    
engine = create_engine(full_url, echo=settings.DEBUG)

def init_db():
    SQLModel.metadata.create_all(engine)

async def connect_db():
    logging.info("Tentando conectar com o DB...")
    retries = 0
    while retries < MAX_RETRIES:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logging.info("Conexão com DB bem-sucedida!")
            return
        except Exception as e:
            retries += 1
            logging.warning(f"Conexão com DB falhou ({retries}/{MAX_RETRIES}): {e}")
            if retries >= MAX_RETRIES:
                logging.error("Número máximo de tentativas atingido.")
                raise e
            await asyncio.sleep(RETRY_DELAY)


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