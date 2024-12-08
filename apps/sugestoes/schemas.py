from typing import TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

from apps.sugestoes.types import Status_Sugestao

if TYPE_CHECKING:
    from database.schemas.users import User
    from database.schemas.problemas import Problema

class Sugestoes_User(SQLModel, table=True):
    sugestao_id: int | None = Field(default = None, foreign_key = "sugestoes.id", primary_key = True)
    user_id:     int | None = Field(default = None, foreign_key = "user.id",      primary_key = True)
    voto: bool

    sugestao: "Sugestoes" = Relationship(back_populates = "votantes")
    user: "User" = Relationship(back_populates = 'sugestoes_votadas')


class Problema_Sugestoes(SQLModel, table=True):
    problema_id: int | None = Field(default = None, foreign_key = 'problema.id',  primary_key = True)
    sugestao_id: int | None = Field(default = None, foreign_key = 'sugestoes.id', primary_key = True)


class Sugestoes(SQLModel, table=True):
    id: int | None = Field(default = None, primary_key = True)
    descricao: str = Field(min_length = 3, max_length = 255)
    status: Status_Sugestao = Status_Sugestao.ativa

    problema_id: int = Field(foreign_key = "problema.id")
    problema: 'Problema' = Relationship(back_populates = 'sugestoes')
    
    autor_id: int = Field(foreign_key = "user.id")
    autor: 'User' = Relationship(back_populates = 'sugestoes_criadas')

    votantes: list['Sugestoes_User'] = Relationship(back_populates = 'sugestao')

    def upvotes(self):
        return [ votante for votante in self.votantes if votante.voto == True ]
    
    def downvotes(self):
        return [ votante for votante in self.votantes if votante.voto == False ]

