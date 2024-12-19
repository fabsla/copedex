from typing import TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from enum import Enum

from database.schemas.problemas import Problema_User, Sugestao_User

if TYPE_CHECKING:
    from database.schemas.problemas import Problema, Sugestao

'''
''  Pessoa
'''
class PessoaBase(SQLModel):
    id: int | None = Field(default = None, primary_key = True)
    nome: str      = Field(default = None, min_length = 3, max_length = 255)
    
class Pessoa (PessoaBase, table=True):
    def __format__():
        return 'Pessoa'

    user_id: int = Field(foreign_key = "user.id")
    user: 'User' = Relationship(back_populates = "pessoa")

'''
''  Role
'''
class RoleEnum(Enum):
    admin  = 3
    editor = 2
    leitor = 1
    guest  = 0

class RoleName(Enum):
    admin  = 'Administrador'
    editor = 'Editor'
    leitor = 'Leitor'
    guest  = 'Convidado'
    
class RoleBase(SQLModel):
    id: int | None    = Field(default = None, primary_key=True)
    display_name: str = Field(default = None, min_length = 3, max_length = 25)

class Role (RoleBase, table=True):
    def __format__():
        return 'Papel'
    pass

'''
''  User
'''
class UserBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    username: str  = Field(default=None, unique=True, min_length = 3, max_length=255)
    
class User(UserBase, table=True):
    def __format__():
        return 'Usuário'
    
    password: str = Field(min_length = 3, max_length=255)
    ativo: bool = Field(default = True)

    pessoa: Pessoa | None = Relationship(back_populates = "user")

    role_id: int | None = Field(foreign_key = "role.id", default = 1)
    role: Role | None   = Relationship()

    problemas: list["Problema"] | None = Relationship(back_populates = "uploaders", link_model = Problema_User)

    sugestoes_criadas: list['Sugestao'] | None = Relationship(back_populates = 'autor')
    sugestoes_votadas: list['Sugestao_User'] | None = Relationship(back_populates = 'user')

    def has_higher_role(self, role: RoleEnum):
        return self.role.id > role.value
        
    def has_role_or_higher(self, role: RoleEnum):
        return self.role.id >= role.value
    
    def has_role(self, role: RoleEnum):
        return self.role.id == role.value
    
    def has_role_or_lower(self, role: RoleEnum):
        return self.role.id <= role.value
    
    def has_lower_role(self, role: RoleEnum):
        return self.role.id < role.value