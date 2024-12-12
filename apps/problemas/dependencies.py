from typing import Annotated
from fastapi import Depends
from database.schemas.problemas import Problema, Tag, Evento, Sugestao
from database.utils import ModelGetter

ProblemaDep = Annotated[Problema, Depends(ModelGetter(Problema))]

EventoDep = Annotated[Evento, Depends(ModelGetter(Evento))]

TagDep = Annotated[Tag, Depends(ModelGetter(Tag))]

SugestaoDep = Annotated[Sugestao, Depends(ModelGetter(Sugestao))]
