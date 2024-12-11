# Base
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Query

# Database
from database.connection import DBSessionDep
from database.utils import delete_row, get_index

# Dependencies
from apps.auth.utils import DBCurrentUserDep
from apps.problemas.dependencies import ProblemaDep

# Schemas
from database.schemas.users import User
from database.schemas.problemas import Evento, Problema, Tag
from apps.problemas.models.requests import EventoCreate, EventoRead, TagRead, TagListQueryParams
from apps.problemas.models.responses import TagSingleResponse, ProblemaFullResponse

# Utils
from policies.utils import Authorizer, check_permissions
from apps.problemas.utils import Problemas, Eventos, Tags

tag_router = APIRouter(
    prefix = '/tags',
    tags = ['tags'],
    responses = { 404: {'description': 'Tag não encontrada'}},
)

@tag_router.get("/")
async def list_tags(*,
    params: Annotated[TagListQueryParams, Query()],
    db: DBSessionDep
) -> TagSingleResponse:
    
    tag = TagRead(**params.model_dump())

    tag_results = Tags.get(
        tag = tag,
        skip = params.skip,
        limit = params.limit,
        db = db
    )

    return tag_results


@tag_router.post("/")
async def store_tags(*,
    tag: Tag,
    session: DBSessionDep
):

    tag_db = Tag(nome = tag.nome)
    
    session.add(tag_db)
    session.commit()

    return { "success": True }


@app.post("/tags/{tag_id}")
async def update_tags(
    tag_id: int,
    nome: str,
    session: DBSessionDep
    ):

    tag = session.get(Tag, tag_id)

    if tag is None:
        return {
            "success": False,
            "message": "Não foram encontradas tags com o id informado!"
        }

    tag.nome = nome

    session.add(tag)
    session.commit()

    return {
        "success": True
    }


@app.delete("/tags/{tag_id}")
async def delete_tags(
    tag_id: int,
    session: DBSessionDep
):
    tag = session.get(Tag, tag_id)

    if tag is None:
        return {
            "success": False,
            "message": "Não foram encontradas tags com o id informado!"
        }
    
    session.delete(tag)
    session.commit()

    return { "success": True }


@app.post("/{problema_id}/atribuir_tags")
async def atribuir_tags(
    problema_id: int,
    tags: list[int],
    session: DBSessionDep
):
    problema = session.get(Problema, problema_id)

    if problema is None:
        return {
            "success": False,
            "message": "Não foram encontrados problemas com o id informado!"
        }

    error_ids = []

    for tag_id in tags:
        tag = session.get(Tag, tag_id)

        if tag is None:
            error_ids.append(tag_id)
            continue

        tag.problemas.append(problema)
        session.add(tag)

    session.commit()