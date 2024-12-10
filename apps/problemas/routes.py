# Base
from typing import Annotated
from fastapi import APIRouter, Depends

# Database
from database.connection import DBSessionDep

# Dependencies
from apps.auth.utils import DBCurrentUserDep
from apps.problemas.dependencies import ProblemaDep

# Schemas
from database.schemas.users import User
from database.schemas.problemas import Evento, Problema, Pessoa, Role, Tag
from apps.problemas.models.requests import EventoCreate, EventoRead, ProblemaRead, ProblemaCreate, TagRead
from apps.problemas.models.responses import ProblemaFullResponse

# Utils
from apps.problemas.utils import Problemas

router = APIRouter(
    prefix = '/problemas',
    tags = ['problemas'],
    responses = { 404: {'description': 'Não encontrado'}}
)

'''
Problemas
'''
@router.get("/problemas")
async def list_problemas(*,
    problema: ProblemaRead | None,
    eventos: list[EventoRead] | None,
    tags: list[TagRead] | None,
    skip: int | None = None,
    limit: int = 100,
    db: DBSessionDep
) -> ProblemaFullResponse:
    
    problemas = Problemas.get(
        problema = problema,
        eventos = eventos,
        tags = tags,
        skip = skip,
        limit = limit,
        db = db
    )

    return problemas


@router.post("/problemas")
async def store_problemas(
    problema: ProblemaCreate,
    evento: EventoCreate,
):
    titulo: str,
    enunciado: str,
    limite_tempo: int | None = None,
    limite_memoria_mb: int | None = None,
    categoria: str | None = None,
    dificuldade: str | None = None,
    autor: str | None = None,
    evento: str | None = None
    problema = Problemas.create(
        titulo=titulo,
        enunciado=enunciado,
        limite_tempo=limite_tempo,
        limite_memoria_mb=limite_memoria_mb,
        categoria=categoria,
        dificuldade=dificuldade,
        autor=autor,
        evento=evento,
    )

    with Session(db_engine) as session:
        session.add(problema)
        session.commit()
        session.refresh(problema)

    return problema


@app.get("/problemas/{id}")
async def read_problemas(id):
    with Session(db_engine) as session:
        # query = select(Problema).where(Problema.id == id)
        # results = session.exec(query).first()
        problema = session.get(Problema, id)

        if problema is None:
            return { "message" : "Não foram encontrados problemas com o id informado!" }

    # problema = list(filter(lambda prob: (prob['id'] == int(id)), problemas))
    return problema


@app.put("/problemas/{problema_id}")
async def update_problemas(problema_id,
        titulo: str,
        enunciado: str,
        limite_tempo: int,
        limite_memoria_mb: int,
        categoria: str,
        dificuldade: str,
        autor: str,
        evento: str
    ):
    with Session(db_engine) as session:
        query = select(Problema).where(Problema.id == problema_id)
        problema = session.exect(query).first()

        if problema is None:
            return { "message" : "Não foram encontrados problemas com o id informado!" }
        
        problema.titulo = titulo
        problema.enunciado = enunciado
        problema.limite_tempo = limite_tempo
        problema.limite_memoria_mb = limite_memoria_mb
        problema.categoria = categoria
        problema.dificuldade = dificuldade
        problema.autor = autor
        problema.evento = evento
        
        session.add(problema)
        session.commit()
        session.refresh(problema)

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

