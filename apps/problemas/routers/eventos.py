# Base
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Query

# Database
from database.connection import DBSessionDep
from database.utils import delete_row, get_index, upsert_row

# Dependencies
from apps.auth.utils import DBCurrentUserDep
from apps.problemas.dependencies import EventoDep

# Schemas
from database.schemas.problemas import Evento
from apps.problemas.models.requests import EventoCreate, EventoRead, EventoListQueryParams
from apps.problemas.models.responses import EventoSingleResponse, ProblemaSingleResponse

# Utils
from policies.utils import Authorizer, check_permissions
from apps.problemas.utils import Eventos

evento_router = APIRouter(
    prefix = '/eventos',
    tags = ['eventos'],
    responses = { 404: {'description': 'Evento não encontrado'}},
)

'''
Eventos
'''
@evento_router.get('/')
async def list_eventos(
    params: Annotated[EventoListQueryParams, Query()],
    db: DBSessionDep,
) -> list[EventoSingleResponse]:
    
    evento = EventoRead(**params.model_dump())

    eventos = Eventos.get(
        evento = evento,
        skip = params.skip,
        limit = params.limit,
        db = db
    )

    return eventos

@evento_router.get("/{id}")
async def read_eventos(
    evento: EventoDep,
    db: DBSessionDep
) -> EventoSingleResponse:
    
    return evento

@evento_router.get('/{id}/problemas')
async def read_evento_problemas(
    evento: EventoDep,
) -> list[ProblemaSingleResponse]:
    
    return evento.problemas

@evento_router.post("/", dependencies=[Depends(Authorizer('evento', 'store'))])
async def store_eventos(
    evento: EventoCreate,
    db: DBSessionDep
) -> EventoSingleResponse:
    evento = Evento(**evento.model_dump())

    try:
        evento_response = upsert_row(model_instance = evento, db = db)
    except:
        raise

    return evento_response


@evento_router.post("/{id}", dependencies=[Depends(Authorizer('evento', 'update'))])
async def update_eventos(
    evento: EventoDep,
    evento_update: EventoCreate,
    db: DBSessionDep
) -> EventoSingleResponse:
    try:
        evento_updated = Eventos.update(
            evento = evento,
            evento_update = evento_update,
            db = db
        )
    except:
        raise

    return evento_updated


@evento_router.delete("/{id}", dependencies=[Depends(Authorizer('evento', 'delete'))])
async def delete_eventos(
    evento: EventoDep,
    db: DBSessionDep
):
    # permitir apenas se evento não possui problemas associados ou apenas marcar como null?
    try:
        delete_row(model_instance = evento, db = db)
    except:
        raise

    return { "success": True }