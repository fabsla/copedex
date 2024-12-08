from typing import TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from database.schemas.users import User, Pessoa, Role
    from apps.sugestoes.schemas import Sugestoes

class Problema_Tag(SQLModel, table=True):
    problema_id: int | None = Field(default = None, foreign_key = "problema.id", primary_key = True)
    tag_id:      int | None = Field(default = None, foreign_key = "tag.id",      primary_key = True)


class Problema_User(SQLModel, table=True):
    problema_id: int | None = Field(default = None, foreign_key = "problema.id", primary_key= True)
    user_id: int | None     = Field(default = None, foreign_key = "user.id",     primary_key= True)


class TagBase(SQLModel):
    id: int | None = Field(default = None, primary_key = True)
    nome: str      = Field(default = None, max_length = 255, min_length = 3)
    
class Tag(TagBase, table=True):
    problemas: list["Problema"] = Relationship(back_populates="tags", link_model=Problema_Tag)


class EventoBase(SQLModel):
    id: int | None = Field(default = None, primary_key = True)
    titulo: str    = Field(default = None, max_length = 255, min_length = 3)

class Evento(EventoBase, table=True):
    problemas: list["Problema"] = Relationship(back_populates = "evento")


class ProblemaBase(SQLModel):
    id: int | None                = Field(default=None, primary_key=True)
    titulo: str                   = Field(default=None, max_length=255, min_length=3)
    enunciado: str                = Field(max_length=255, min_length=3)
    limite_tempo: int | None      = None
    limite_memoria_mb: int | None = None
    categoria: str                = Field(max_length=255, min_length=3)
    dificuldade: str | None       = Field(default=None, max_length=255, min_length=3)
    autor: int | None             = None

class Problema(ProblemaBase, table=True):
    uploaders: list['User'] | None    = Relationship(back_populates = "problemas", link_model = Problema_User)

    evento_id: int | None         = Field(default=None, foreign_key="evento.id")
    evento: Evento | None = Relationship(back_populates = "problemas")

    tags:   list[Tag]    | None = Relationship(back_populates = "problemas", link_model = Problema_Tag)

    sugestoes: list['Sugestoes'] | None = Relationship(back_populates = "problema")