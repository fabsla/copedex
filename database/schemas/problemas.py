from typing import TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from enum import Enum

if TYPE_CHECKING:
    from database.schemas.users import User, Pessoa, Role

class Status_Sugestao(str, Enum):
    ativa     = 'ativa'     # padrao
    cancelada = 'cancelada' # cancelada por autor da sugestao

    # acoes por proprietario do problema
    rejeitada = 'rejeitada' # numero de votos negativos > positivos
    aceita    = 'aceita'    # aceita mas ainda nao implementada
    aplicada  = 'aplicada'  # aceita e implementada


class Problema_Tag(SQLModel, table=True):
    problema_id: int | None = Field(default = None, foreign_key = "problema.id", primary_key = True)
    tag_id:      int | None = Field(default = None, foreign_key = "tag.id",      primary_key = True)


class Problema_User(SQLModel, table=True):
    problema_id: int | None = Field(default = None, foreign_key = "problema.id", primary_key= True)
    user_id: int | None     = Field(default = None, foreign_key = "user.id",     primary_key= True)


class TagBase(SQLModel):
    id: int | None = Field(default = None, primary_key = True)
    
class Tag(TagBase, table=True):
    nome: str = Field(default = None, max_length = 255)
    problemas: list["Problema"] = Relationship(back_populates="tags", link_model=Problema_Tag)


class EventoBase(SQLModel):
    id: int | None = Field(default = None, primary_key = True)

class Evento(EventoBase, table=True):
    titulo: str = Field(default = None, max_length = 255)
    problemas: list["Problema"] = Relationship(back_populates = "evento")


class ProblemaBase(SQLModel):
    id: int | None                = Field(default=None, primary_key=True)
    autor: str | None             = Field(default=None, min_length=3, max_length=255)
    dificuldade: str | None       = Field(default=None, max_length=255, min_length=3)
    limite_tempo: int | None      = None
    limite_memoria_mb: int | None = None

class Problema(ProblemaBase, table=True):
    titulo: str    = Field(default=None, max_length=255, min_length=3)
    enunciado: str = Field()
    categoria: str = Field(max_length=255, min_length=3)

    uploaders: list['User'] | None = Relationship(back_populates = "problemas", link_model = Problema_User)

    evento_id: int | None = Field(default=None, foreign_key="evento.id")
    evento: Evento | None = Relationship(back_populates = "problemas")

    tags: list[Tag] | None = Relationship(back_populates = "problemas", link_model = Problema_Tag)

    sugestoes: list['Sugestao'] | None = Relationship(back_populates = "problema")


class Sugestao_User(SQLModel, table=True):
    sugestao_id: int | None = Field(default = None, foreign_key = "sugestao.id", primary_key = True)
    user_id:     int | None = Field(default = None, foreign_key = "user.id",     primary_key = True)
    voto: bool

    sugestao: "Sugestao" = Relationship(back_populates = "votantes")
    user: "User" = Relationship(back_populates = 'sugestoes_votadas')

class SugestaoBase(SQLModel):
    id: int | None = Field(default = None, primary_key = True)
    descricao: str = Field(min_length = 3, max_length = 255)
    status: Status_Sugestao = Status_Sugestao.ativa

class Sugestao(SugestaoBase, table=True):
    problema_id: int = Field(foreign_key = "problema.id")
    problema: 'Problema' = Relationship(back_populates = 'sugestoes')
    
    autor_id: int = Field(foreign_key = "user.id")
    autor: 'User' = Relationship(back_populates = 'sugestoes_criadas')

    votantes: list['Sugestao_User'] = Relationship(back_populates = 'sugestao')
    
    def upvotes(self):
        return [ votante for votante in self.votantes if votante.voto == True ]
    
    @property
    def upvotes_count(self):
        return len(self.upvotes())
    
    def downvotes(self):
        return [ votante for votante in self.votantes if votante.voto == False ]
    
    @property
    def downvotes_count(self):
        return len(self.downvotes())
