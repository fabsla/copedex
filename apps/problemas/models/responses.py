from pydantic import BaseModel
from database.schemas.problemas import EventoBase, ProblemaBase, TagBase, SugestoesBase
from sqlmodel import Field

from database.schemas.users import UserBase, Pessoa, Role

class ProblemaSingleResponse(ProblemaBase):
    titulo: str    = Field(default=None, max_length=255, min_length=3)
    enunciado: str = Field(max_length=255, min_length=3)
    categoria: str = Field(max_length=255, min_length=3)

class TagSingleResponse(TagBase):
    nome: str

class TagFullResponse(TagSingleResponse):
    problemas: list[ProblemaSingleResponse]

class EventoSingleResponse(EventoBase):
    titulo: str | None

class EventoFullResponse(EventoSingleResponse):
    problemas: list[ProblemaSingleResponse]
    
class ProblemaFullResponse(ProblemaBase):
    titulo: str    = Field(default=None, max_length=255, min_length=3)
    enunciado: str = Field(max_length=255, min_length=3)
    categoria: str = Field(max_length=255, min_length=3)
    uploaders: list[UserBase] | None
    evento: EventoSingleResponse | None
    tags: list[TagSingleResponse] | None
    # sugestoes: list['SugestoesResponse']

class SugestaoSingleResponse(SugestoesBase):
    problema_id: int
    autor_id: int
    upvotes_count: int
    downvotes_count: int

class SugestaoFullResponse(SugestaoSingleResponse):
    problema: list[ProblemaSingleResponse]