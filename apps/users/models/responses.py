from pydantic import BaseModel
from database.schemas.users import UserBase
from database.schemas.users import UserBase, Pessoa, Role
from database.schemas.problemas import Problema_User, Sugestao_User, Sugestao, Problema
from sqlmodel import Relationship, Field

class UserRestoreResponse(BaseModel):
    sucesso: bool
    user: UserBase

class UserRead(UserBase):
    ativo: bool = Field(default = True)

    pessoa: Pessoa | None = Relationship(back_populates = "user")

    role_id: int | None = Field(foreign_key = "role.id", default = 1)
    role: Role | None   = Relationship()

    problemas: list["Problema"] | None = Relationship(back_populates = "uploaders", link_model = Problema_User)

    sugestoes_criadas: list['Sugestao'] | None = Relationship(back_populates = 'autor')
    sugestoes_votadas: list['Sugestao_User'] | None = Relationship(back_populates = 'user')