# Base
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Query

# Database
from database.connection import DBSessionDep
from database.utils import delete_row

# Dependencies
from apps.auth.utils import DBCurrentUserDep
from apps.problemas.dependencies import SugestaoDep

# Schemas
from database.schemas.users import User
from database.schemas.problemas import Status_Sugestao
from apps.problemas.models.requests import SugestaoRead, SugestaoListQueryParams
from apps.problemas.models.responses import SugestaoSingleResponse

# Utils
from policies.utils import Authorizer, check_permissions
from apps.problemas.utils import Sugestoes

sugestao_router = APIRouter(
    prefix = '/sugestoes',
    tags = ['sugestoes'],
    responses = { 404: {'description': 'Sugestão não encontrada'}},
)

@sugestao_router.get("/", dependencies=[Depends(Authorizer('sugestao', 'index'))])
async def list_sugestoes(*,
    params: SugestaoListQueryParams,
    db: DBSessionDep
) -> list[SugestaoSingleResponse]:
    
    sugestao = SugestaoRead(**params.model_dump())

    try:
        sugestoes_results = Sugestoes.get(
            sugestao = sugestao,
            skip = params.skip,
            limit = params.limit,
            db = db
        )
    except:
        raise
    
    return sugestoes_results


@sugestao_router.get("/{id}/votos", dependencies=[Depends(Authorizer('sugestao', 'view'))])
async def read_votos_sugestao(
    sugestao: SugestaoDep,
    db: DBSessionDep,
) -> SugestaoSingleResponse:
    
    return sugestao


@sugestao_router.post("/{id}/votar", dependencies=[Depends(Authorizer('sugestao', 'votar'))])
async def votar_sugestao(
    sugestao: SugestaoDep,
    voto: bool,
    current_user: DBCurrentUserDep,
    db: DBSessionDep
) -> SugestaoSingleResponse:
    
    try:
        sugestao_result = Sugestoes.votar(
            sugestao = sugestao,
            voto = voto,
            user = current_user,
            db = db
        )
    except:
        raise

    return sugestao_result


@sugestao_router.patch("/{id}/status", dependencies=[Depends(Authorizer('sugestao', 'update'))])
async def alterar_status_sugestao(
    sugestao: SugestaoDep,
    status: Status_Sugestao,
    current_user: DBCurrentUserDep,
    db: DBSessionDep
) -> SugestaoSingleResponse:
    
    check_permissions(model = 'sugestao', ability = 'update', user = current_user, problema = sugestao.problema)

    try:
        sugestao_result = Sugestoes.update_status(
            sugestao = sugestao,
            status = status,
            db = db,
        )
    except:
        raise

    return sugestao_result
    


@sugestao_router.delete("/{id}", dependencies=[Depends(Authorizer('sugestao', 'delete'))])
async def delete_sugestao(
    sugestao: SugestaoDep,
    current_user: DBCurrentUserDep,
    db: DBSessionDep
):
    check_permissions(model = 'sugestao', ability = 'delete', user = current_user, sugestao = sugestao)
    
    try:
        delete_row(model_instance = sugestao, db = db)
    except:
        raise

    return { 'sucesso': True }
    