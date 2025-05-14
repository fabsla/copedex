from database.schemas.users import UserBase
from sqlmodel import Field
from sqlmodel import Field
from enum import Enum

class RoleOptions(Enum):
    admin  = 'Administrador'
    editor = 'Editor'
    leitor = 'Leitor'

class UserCreate(UserBase):
    password: str = Field(min_length = 3, max_length=255)
