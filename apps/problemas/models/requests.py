from database.schemas.problemas import ProblemaBase, EventoBase, TagBase
from sqlmodel import Field

class ProblemaCreate(ProblemaBase):
    titulo: str    = Field(default=None, max_length=255, min_length=3)
    enunciado: str = Field(max_length=255, min_length=3)
    categoria: str = Field(max_length=255, min_length=3)

class EventoCreate(EventoBase):
    titulo: str = Field(default = None, max_length = 255, min_length = 3)

class TagCreate(TagBase):
    nome: str = Field(default = None, max_length = 255, min_length = 3)

class ProblemaRead(ProblemaBase):
    categoria: str | None = None
    enunciado: str | None = None
    evento: str = None
    limite_tempo_inf: int | None = None
    limite_tempo_sup: int | None = None
    limite_memoria_inf: int | None = None
    limite_memoria_sup: int | None = None
    titulo: str | None = None

class EventoRead(EventoBase):
    titulo: list[str] | None = None

class TagRead(TagBase):
    nome: list[str] | None = None