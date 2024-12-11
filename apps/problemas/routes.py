# Base
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

# Database
from database.connection import DBSessionDep
from database.utils import upsert_row

# Dependencies
from apps.auth.utils import DBCurrentUserDep
from apps.problemas.dependencies import ProblemaDep

# Schemas
from database.schemas.users import User
from database.schemas.problemas import Evento, Problema, Pessoa, Role, Tag
from apps.problemas.models.requests import EventoCreate, EventoRead, ProblemaRead, ProblemaCreate, TagRead
from apps.problemas.models.responses import ProblemaFullResponse

# Utils
from policies.utils import Authorizer, check_permissions
from apps.problemas.utils import Problemas

router = APIRouter(
    prefix = '/problemas',
    tags = ['problemas'],
    responses = { 404: {'description': 'Não encontrado'}}
)

'''
Problemas
'''
@router.get("/")
async def list_problemas(*,
    problema: ProblemaRead | None,
    eventos: list[EventoRead] | None,
    tags: list[TagRead] | None,
    skip: int | None = None,
    limit: int = 100,
    db: DBSessionDep
) -> list[ProblemaFullResponse]:
    
    problemas = Problemas.get(
        problema = problema,
        eventos = eventos,
        tags = tags,
        skip = skip,
        limit = limit,
        db = db
    )

    return problemas


@router.post("/", dependencies=[Depends(Authorizer('problema', 'store'))])
async def store_problemas(
    problema: ProblemaCreate,
    evento: EventoRead,
    tags: TagRead,
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


@router.get("/problemas/{id}")
async def read_problemas(
    problema: ProblemaDep,
) -> ProblemaFullResponse:
    return problema


@router.put("/problemas/{id}",, dependencies=[Depends(Authorizer('problema', 'update'))])
async def update_problemas(
    problema: ProblemaDep,
    problema_update: ProblemaRead,
    evento_update: EventoRead,
    tags: list[TagRead],
    db: DBSessionDep,
) -> ProblemaFullResponse:

    check_permissions(model = 'problema', ability = 'update', problema = problema)
    
    problema = Problemas.update(
        problema = problema,
        problema_update = problema_update,
        evento_update = evento_update,
        tags = tags,
        db = db
    )
    # problema.titulo = problema_update.titulo
    # problema.enunciado = problema_update.enunciado
    # problema.limite_tempo = problema_update.limite_tempo
    # problema.limite_memoria_mb = problema_update.limite_memoria_mb
    # problema.categoria = problema_update.categoria
    # problema.dificuldade = problema_update.dificuldade
    # problema.autor = problema_update.autor
    # problema.evento = problema_update.evento
    
    # problema = upsert_row(
    #     model_instance
    # )

    return problema


@app.patch("/problemas/{problema_id}")
async def partial_update_problemas(problema_id,
        titulo: str | None = None,
        enunciado: str | None = None,
        limite_tempo: int | None = None,
        limite_memoria_mb: int | None = None,
        categoria: str | None = None,
        dificuldade: str | None = None,
        autor: str | None = None,
        evento: str | None = None
    ):
    with Session(db_engine) as session:
        query = select(Problema).where(Problema.id == problema_id)
        problema = session.exect(query).first()

        if problema is None:
            return { "message" : "Não foram encontrados problemas com o id informado!" }
        
        if titulo:
            problema.titulo = titulo
        if enunciado:
            problema.enunciado = enunciado
        if limite_tempo:
            problema.limite_tempo = limite_tempo
        if limite_memoria_mb:
            problema.limite_memoria_mb = limite_memoria_mb
        if categoria:
            problema.categoria = categoria
        if dificuldade:
            problema.dificuldade = dificuldade
        if autor:
            problema.autor = autor
        if evento:
            problema.evento = evento
        
        session.add(problema)
        session.commit()
        session.refresh(problema)

    return problema


@app.delete("/problemas/{problema_id}")
async def delete_problemas_autor(problema_id):
    with Session(db_engine) as session:
        problema = session.exec(select(Problema).where(Problema.id == problema_id)).first()

        if problema:
            session.delete(problema)
            session.commit()

    return { "message": "success" }


'''
Problemas de autor
'''
@app.get("/usuarios/{user_id}/problemas")
async def index_problemas_autor(user_id: int, session: Session = Depends(db_engine.get_session)):

    query = select(User).where(User.id == user_id)
    user = session.exec(query).first()

    if not user:
        return {}
    
    problemas = user.problemas

    return problemas

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

