from pydantic import BaseModel
from database.schemas.problemas import EventoBase, ProblemaBase, TagBase
from sqlmodel import Field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from database.schemas.users import UserBase, Pessoa, Role
    from apps.sugestoes.schemas import Sugestoes

class TagSingleResponse(TagBase):
    nome: str

class TagFullResponse(TagSingleResponse):
    problemas: list['ProblemaSingleResponse']

class EventoSingleResponse(EventoBase):
    titulo: str | None

class EventoFullResponse(EventoSingleResponse):
    problemas: list['ProblemaSingleResponse']

class ProblemaSingleResponse(ProblemaBase):
    titulo: str    = Field(default=None, max_length=255, min_length=3)
    enunciado: str = Field(max_length=255, min_length=3)
    categoria: str = Field(max_length=255, min_length=3)
    
class ProblemaFullResponse(ProblemaBase):
    titulo: str    = Field(default=None, max_length=255, min_length=3)
    enunciado: str = Field(max_length=255, min_length=3)
    categoria: str = Field(max_length=255, min_length=3)
    uploaders: list['UserBase'] | None
    evento: EventoSingleResponse
    tags: list[TagSingleResponse] | None
    # sugestoes: list['SugestoesResponse']