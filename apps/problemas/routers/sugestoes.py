# Base
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Query

# Database
from database.connection import DBSessionDep
from database.utils import delete_row, get_index, upsert_row

# Dependencies
from apps.auth.utils import DBCurrentUserDep
from apps.problemas.dependencies import ProblemaDep, SugestaoDep

# Schemas
from database.schemas.users import User
from database.schemas.problemas import Problema, Status_Sugestao
from apps.problemas.models.requests import SugestaoRead, SugestaoCreate, SugestaoListQueryParams
from apps.problemas.models.responses import SugestaoSingleResponse, SugestaoFullResponse, ProblemaSingleResponse

# Utils
from policies.utils import Authorizer, check_permissions
from apps.problemas.utils import Sugestoes

sugestao_router = APIRouter(
    prefix = '/sugestoes',
    tags = ['sugestoes'],
    responses = { 404: {'description': 'Sugestão não encontrada'}},
)

@sugestao_router.get("/")
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


@sugestao_router.get("/{id}/votos")
async def read_votos_sugestao(
    sugestao: SugestaoDep,
    db: DBSessionDep,
) -> SugestaoSingleResponse:
    
    return sugestao


@sugestao_router.post("/{id}/votar")
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


@sugestao_router.patch("/{id}/status")
async def alterar_status_sugestao(
    sugestao: SugestaoDep,
    status: Status_Sugestao,
    db: DBSessionDep
) -> SugestaoSingleResponse:
    try:
        sugestao_result = Sugestoes.update_status(
            sugestao = sugestao,
            status = status,
            db = db,
        )
    except:
        raise

    return sugestao_result
    


@app.delete("/sugestoes/{sugestao_id}")
async def delete_sugestao(
    sugestao_id: int,
    session: DBSessionDep
):
    query = select(Sugestoes).where(Sugestoes.id == sugestao_id)
    sugestao = session.exec(query).first()
    
    session.delete(sugestao)
    session.commit()
    