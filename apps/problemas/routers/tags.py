# Base
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Query

# Database
from database.connection import DBSessionDep
from database.utils import delete_row, get_index, upsert_row

# Dependencies
from apps.auth.utils import DBCurrentUserDep
from apps.problemas.dependencies import ProblemaDep, TagDep

# Schemas
from database.schemas.users import User
from database.schemas.problemas import Evento, Problema, Tag
from apps.problemas.models.requests import TagCreate, TagRead, TagListQueryParams
from apps.problemas.models.responses import TagSingleResponse, ProblemaSingleResponse

# Utils
from policies.utils import Authorizer, check_permissions
from apps.problemas.utils import Problemas, Eventos, Tags

tag_router = APIRouter(
    prefix = '/tags',
    tags = ['tags'],
    responses = { 404: {'description': 'Tag não encontrada'}},
)

@tag_router.get("/", dependencies=[Depends(Authorizer('tag', 'read_any'))])
async def list_tags(*,
    params: Annotated[TagListQueryParams, Query()],
    db: DBSessionDep,
) -> list[TagSingleResponse]:
    
    tag = TagRead(**params.model_dump())

    tag_results = Tags.get(
        tag = tag,
        skip = params.skip,
        limit = params.limit,
        db = db
    )

    return tag_results

@tag_router.get('/{id}/problemas', dependencies=[Depends(Authorizer('tag', 'read')), Depends(Authorizer('problema', 'read_any'))])
async def read_tag_problemas(
    tag: TagDep,
) -> list[ProblemaSingleResponse]:
    
    return tag.problemas

@tag_router.post("/")
async def store_tags(*,
    tag: TagCreate,
    db: DBSessionDep
) -> TagSingleResponse:

    tag = Tag(**tag.model_dump())
    
    try:
        tag_result = upsert_row(model_instance = tag, db = db)
    except:
        raise

    return tag_result


@tag_router.patch("/{id}")
async def update_tags(
    tag: TagDep,
    tag_update: TagCreate,
    db: DBSessionDep
) -> TagSingleResponse:

    try:
        tag_updated = Tags.update(
            tag = tag,
            tag_update = tag_update,
            db = db
        )
    except:
        raise

    return tag_updated


@tag_router.delete("/{id}")
async def delete_tags(
    tag: TagDep,
    db: DBSessionDep
):
    try:
        delete_row(model_instance = tag, db = db)    
    except:
        raise

    return { "success": True }
