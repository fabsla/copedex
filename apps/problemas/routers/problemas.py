# Base
from fastapi import APIRouter, Query, Depends
from typing import Annotated

# Database
from database.connection import DBSessionDep
from database.utils import delete_row

# Dependencies
from apps.auth.utils import DBCurrentUserDep
from apps.problemas.dependencies import ProblemaDep

# Schemas
from apps.problemas.models.requests import EventoBase, EventoRead, ProblemaRead, ProblemaCreate, ProblemaUpdate, TagBase, TagRead, ProblemaListQueryParams, SugestaoCreate
from apps.problemas.models.responses import ProblemaFullResponse, SugestaoSingleResponse

# Utils
from policies.utils import Authorizer, check_permissions
from apps.problemas.utils import Problemas, Sugestoes

problema_router = APIRouter(
    prefix = '/problemas',
    tags = ['problemas'],
    responses = { 404: {'description': 'Problema não encontrado'}},
)

'''
Problemas
'''
@problema_router.get("/")
async def list_problemas(*,
    params: Annotated[ProblemaListQueryParams, Query()],
    db: DBSessionDep
) -> list[ProblemaFullResponse]:
    
    problema = ProblemaRead(**params.model_dump())

    problemas = Problemas.get(
        problema = problema,
        eventos = params.eventos,
        tags = params.tags,
        skip = params.skip,
        limit = params.limit,
        db = db
    )

    return problemas


@problema_router.post("/", dependencies=[Depends(Authorizer('problema', 'store'))])
async def store_problemas(*,
    problema: ProblemaCreate,
    evento: EventoRead | None = None,
    tags: list[TagRead] | None = None,
    current_user: DBCurrentUserDep,
    db: DBSessionDep,
) -> ProblemaFullResponse:
    
    problema = Problemas.create(
        problema = problema,
        evento = evento,
        tags = tags,
        current_user = current_user,
        db = db
    )

    return problema


@problema_router.get("/{id}")
async def read_problemas(
    problema: ProblemaDep,
) -> ProblemaFullResponse:
    return problema


@problema_router.patch("/{id}", dependencies=[Depends(Authorizer('problema', 'update'))])
async def update_problemas(*,
    problema: ProblemaDep,
    problema_update: ProblemaUpdate | None = None,
    evento_update: EventoRead | None = None,
    tags: list[TagRead] | None = None,
    current_user: DBCurrentUserDep,
    db: DBSessionDep,
) -> ProblemaFullResponse:
    
    check_permissions(model = 'problema', ability = 'update', user = current_user, problema = problema)
    
    problema_updated = Problemas.update(
        problema = problema,
        problema_update = problema_update,
        evento_update = evento_update,
        tags = tags,
        db = db
    )

    return problema_updated


@problema_router.delete("/{id}", dependencies=[Depends(Authorizer('problema', 'delete'))])
async def delete_problemas_autor(
    problema: ProblemaDep,
    current_user: DBCurrentUserDep,
    db: DBSessionDep,
):
    check_permissions(model = 'problema', ability = 'delete', user = current_user, problema = problema)

    try:
        delete_row(model_instance = problema, db = db)
    except:
        raise

    return { 'sucesso': True }

@problema_router.post("/{id}/atribuir_tags", dependencies=[Depends(Authorizer('problema', 'update'))])
async def atribuir_tags(
    problema: ProblemaDep,
    tags: list[TagBase],
    current_user: DBCurrentUserDep,
    db: DBSessionDep
):
    check_permissions(
        model = 'problema',
        ability = 'update',
        user = current_user,
        problema = problema
    )

    try:
        tags, errors = Problemas.atribuir_tags(
            problema = problema,
            tags = tags,
            db = db
        )
    except:
        raise

    return {"tags_atribuídas": tags, "tags_nao_encontradas": errors}

@problema_router.post("/{id}/desvincular_tags", dependencies=[Depends(Authorizer('problema', 'update'))])
async def desvincular_tags(
    problema: ProblemaDep,
    tags: list[TagBase],
    current_user: DBCurrentUserDep,
    db: DBSessionDep
):
    check_permissions(
        model = 'problema',
        ability = 'update',
        user = current_user,
        problema = problema
    )

    try:
        Problemas.desvincular_tags(
            problema = problema,
            tags = tags,
            db = db
        )
    except:
        raise

    return { "success": True }

@problema_router.post("/{id}/vincular_evento", dependencies=[Depends(Authorizer('problema', 'update'))])
async def vincular_evento(
    problema: ProblemaDep,
    evento: EventoBase,
    current_user: DBCurrentUserDep,
    db: DBSessionDep
):
    check_permissions(
        model = 'problema',
        ability = 'update',
        user = current_user,
        problema = problema
    )

    try:
        Problemas.vincular_evento(
            problema = problema,
            evento = evento,
            db = db
        )
    except:
        raise

    return { "success": True }

@problema_router.post("/{id}/desvincular_evento", dependencies=[Depends(Authorizer('problema', 'update'))])
async def desvincular_evento(
    problema: ProblemaDep,
    current_user: DBCurrentUserDep,
    db: DBSessionDep
):
    check_permissions(
        model = 'problema',
        ability = 'update',
        user = current_user,
        problema = problema
    )

    try:
        Problemas.desvincular_evento(
            problema = problema,
            db = db
        )
    except:
        raise

    return { "success": True }

@problema_router.post("/{id}/sugestoes", dependencies=[Depends(Authorizer('sugestao', 'store'))])
async def store_sugestao(
    problema: ProblemaDep,
    sugestao: SugestaoCreate,
    current_user: DBCurrentUserDep,
    db: DBSessionDep
) -> SugestaoSingleResponse:
    
    try:
        sugestao_result = Sugestoes.create(
            sugestao = sugestao,
            problema = problema,
            current_user = current_user,
            db = db
        )
    except:
        raise

    return sugestao_result
