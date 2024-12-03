from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
import dotenv
import os

dotenv.load_dotenv('./.env')

class DatabaseSettings(BaseSettings):
    CONNECTOR: str = os.getenv('DATABASE_CONNECTOR')
    HOST: str = os.getenv('DATABASE_HOST')
    PORT: str = os.getenv('DATABASE_PORT')
    DB_NAME: str = os.getenv('DATABASE_DB_NAME')
    DB_USER: str = os.getenv('DATABASE_USER')
    DB_PASSWORD: str = os.getenv('DATABASE_PASSWORD')

class AuthenticationSettings(BaseSettings):
    SECRET_KEY: str = os.getenv('SECRET_KEY')
    ALGORITHM: str = os.getenv('ALGORITHM')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 30)

class CORSSettings(BaseSettings):
    ALLOWED_ORIGINS: list[str] = [
        'http://localhost',
        'https://localhost'
    ]

class Settings(BaseSettings):
    DEBUG: bool = os.getenv('DEBUG', True)
    APP_NAME: str = os.getenv('APP_NAME', 'CoPR - Contest Problem Radar')
    
    auth: AuthenticationSettings = AuthenticationSettings()
    cors: CORSSettings = CORSSettings()
    database: DatabaseSettings = DatabaseSettings()

# @lru_cache
# def get_settings():
#     return config.Settings()

settings = Settings()
