from pydantic import BaseModel
from database.schemas.users import UserBase
from database.schemas.users import UserBase, Pessoa, Role
from database.schemas.problemas import Problema_User, Sugestao_User, Sugestao, Problema
from sqlmodel import Relationship, Field

class UserRestoreResponse(BaseModel):
    sucesso: bool
    user: UserBase

class UserRead(UserBase):
    ativo: bool

    pessoa: Pessoa | None
    role: Role | None

    # problemas: list["Problema"] | None

    sugestoes_criadas: list['Sugestao'] | None
    sugestoes_votadas: list['Sugestao_User'] | None