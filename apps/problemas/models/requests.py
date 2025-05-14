from database.schemas.problemas import ProblemaBase, EventoBase, TagBase, Status_Sugestao, SugestaoBase
from sqlmodel import Field, SQLModel
from pydantic import BaseModel

class ProblemaCreate(BaseModel):
    titulo: str    = Field(default=None, max_length=255, min_length=3)
    enunciado: str = Field(min_length=0)
    categoria: str = Field(max_length=255, min_length=3)
    autor: str | None             = None
    dificuldade: str | None       = Field(default=None, max_length=255, min_length=3)
    limite_tempo: int | None      = None
    limite_memoria_mb: int | None = None

class EventoCreate(EventoBase):
    titulo: str = Field(default = None, max_length = 255, min_length = 3)

class TagCreate(TagBase):
    nome: str = Field(default = None, max_length = 255, min_length = 3)

class SugestaoCreate(BaseModel):
    descricao: str = Field(min_length = 3, max_length = 255)

class ProblemaUpdate(SQLModel):
    titulo: str | None            = None
    enunciado: str | None         = None
    categoria: str | None         = None
    autor: str | None             = None
    dificuldade: str | None       = Field(default=None, max_length=255, min_length=3)
    limite_tempo: int | None      = None
    limite_memoria_mb: int | None = None

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
    titulo: str | None = None

class TagRead(TagBase):
    nome: str | None = None

class SugestaoRead(BaseModel):
    id: int | None = None
    problema_id: int | None = None
    autor_id: int | None = None
    descricao: str | None = None
    status: Status_Sugestao | None = Status_Sugestao.ativa
    upvotes_limite_inf: int | None = None
    upvotes_limite_sup: int | None = None
    downvotes_limite_inf: int | None = None
    downvotes_limite_sup: int | None = None

class ListCommonQueryParams(BaseModel):
    skip: int = Field(default= 0)
    limit: int = Field(default=100)

class TagListQueryParams(ListCommonQueryParams):
    nome: str | None = Field(default=None)
class EventoListQueryParams(ListCommonQueryParams):
    titulo: str | None = None

class ProblemaListQueryParams(ListCommonQueryParams):
    titulo: str | None = None
    categoria: str | None = None
    enunciado: str | None = None
    limite_tempo_inf: int | None = None
    limite_tempo_sup: int | None = None
    limite_memoria_inf: int | None = None
    limite_memoria_sup: int | None = None

    autor: str | None       = None
    dificuldade: str | None = None

    eventos: list[str] = None
    tags: list[str] = None

class SugestaoListQueryParams(ListCommonQueryParams):
    problema_id: int | None = Field(default = None, gt = 0)
    autor_id: int | None = Field(default = None, gt = 0)
    descricao: str | None = Field(default = None, min_length = 3, max_length = 255)
    status: Status_Sugestao | None = None

    upvotes_limite_inf: int | None = None
    upvotes_limite_sup: int | None = None
    downvotes_limite_inf: int | None = None
    downvotes_limite_sup: int | None = None