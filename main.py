# Main
import uvicorn # para testes

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from typing import Annotated

# DB
from database.connection import init_db, DBSessionDep
from database.seeders.roles import RoleSeeder

# App
from config import settings

# Dependencies
from apps.auth.dependencies import oauth2_scheme

# Models

# Schemas
from apps.sugestoes.types import Status_Sugestao
from apps.sugestoes.schemas import Sugestoes, Sugestoes_User, Problema_Sugestoes

from database.schemas.auth import Token, TokenData
from database.schemas.users import Pessoa, Role, User
from database.schemas.problemas import Evento, Problema, Tag, Problema_User, Problema_Tag

# Routers
from apps.auth.routes import router as auth_router
from apps.users.routes import router as user_router

# Utils

# import policies

# Lifespan: linhas antes do 'yield' serão executadas on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    RoleSeeder.seed_db()
    yield

# init
app = FastAPI(lifespan = lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins     = settings.cors.ALLOWED_ORIGINS.split(','), # lista de origens permitidas
    allow_credentials = True, # permite cookies
    allow_methods     = ['*'], # lista de metodos HTTP permitidos 
    allow_headers     = ['*'], # lista de headers HTTP permitidos
)

# Routers
app.include_router(auth_router)
app.include_router(user_router)

@app.get("/")
async def root():
    return {
        "message": 'bem-vindo'
    }

'''
Testes
'''
# @app.get("/teste")
# async def list_test(
#     id: int,
#     token: Annotated[str, Depends(oauth2_scheme)],
#     session: DBSessionDep,
# ):
#     permission = can('User', 'create', 'admin')
#     return { 'message' : permission }


'''
Tags
'''
@app.get("/tags")
async def list_tags(*,
    tag_id: int | None = None,
    nome: str | None = None,
    session: DBSessionDep
    ):
    
    query = select(Tag)

    if tag_id:
        query = query.where(Tag.id == tag_id)
    if nome:
        query = query.where(Tag.nome == nome)
    
    tags = session.exec(query).all()

    return tags


@app.post("/tags")
async def store_tags(
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


'''
Eventos
'''
@app.get("/eventos")
async def list_eventos(*,
    evento_id: int | None = None,
    titulo: str | None = None,
    session: DBSessionDep
    ):
    
    query = select(Evento)
    
    if evento_id:
        query = query.where(Evento.id == evento_id)
    if titulo:
        query = query.where(Evento.titulo == titulo)
    
    eventos = session.exec(query).all()

    return eventos


@app.get("/eventos/{evento_id}")
async def read_eventos(
    evento_id: int,
    session: DBSessionDep
):
    evento = session.get(Evento, evento_id)

    if evento is None:
        return {
            "success": False,
            "message": "Não foram encontrados eventos com o id informado!"
        }
    
    return evento


@app.post("/eventos")
async def store_eventos(
    evento: Evento,
    session: DBSessionDep
):
    evento_db = Evento(
        titulo = evento.titulo
    )

    session.add(evento_db)
    session.commit()

    return { "success": True }


@app.post("/eventos/{evento_id}")
async def update_eventos(
    evento_id: int,
    titulo: str,
    session: DBSessionDep
):
    evento = session.get(Evento, evento_id)

    if evento is None:
        return {
            "success": False,
            "message": "Não foram encontrados eventos com o id informado!"
        }
    
    evento.titulo = titulo
    
    session.add(evento)
    session.commit()

    return { "success": True }


@app.delete("/eventos/{evento_id}")
async def delete_eventos(
    evento_id: int,
    session: DBSessionDep
    ):
    
    evento = session.get(Evento, evento_id)

    if evento is None:
        return {
            "success": False,
            "message": "Não foram encontrados eventos com o id informado!"
        }
    
    session.delete(evento)
    session.commit()

    return { "success": True }


'''
Sugestões
'''
@app.get("/sugestoes")
async def list_sugestoes(*,
    problema_id: int | None = None,
    status: Status_Sugestao | None = None,
    session: DBSessionDep
    ):
    
    query = select(Sugestoes)
    
    if problema_id:
        query = query.where(Sugestoes.problema_id == problema_id)    
    if status:
        query = query.where(Sugestoes.status == status)

    sugestoes = session.exec(query).all()

    return sugestoes


@app.get("/sugestoes/{sugestao_id}/votos")
async def read_votos_sugestao(sugestao_id: int, session: DBSessionDep):

    query = select(Sugestoes).where(Sugestoes.id == sugestao_id)
    sugestao = session.exec(query).first()

    votos = {}

    if sugestao:
        upvotes = sugestao.upvotes()
        downvotes = sugestao.downvotes()
        votos = {
            "upvotes" : len(upvotes),
            "downvotes" : len(downvotes)
        }

    return votos


@app.post("/sugestoes")
async def store_sugestao(
    sugestao: Sugestoes, # Substituir por model do pydantic
    session: DBSessionDep
):
    sugestao_db = Sugestoes(
        descricao = sugestao.descricao,
        problema_id = sugestao.problema_id
    )

    session.add(sugestao_db)
    session.commit()

    return { 'success': True }


@app.post("/sugestoes/{sugestao_id}/votar")
async def votar_sugestao(
    sugestao_id: int,
    voto: bool,
    session: DBSessionDep
):
    query = select(Sugestoes).where(Sugestoes.id == sugestao_id)
    sugestao = session.exec(query).first()

    # get user

    voto_link = Sugestoes_User(
        sugestao = sugestao,
        user = None,
        voto = voto
    )

    sugestao.votantes.append(voto_link)
    session.add(sugestao)
    session.commit()


@app.patch("/sugestoes/{sugestao_id}/status")
async def alterar_status_sugestao(
    sugestao_id: int,
    status: Status_Sugestao,
    session: DBSessionDep
):
    query = select(Sugestoes).where(Sugestoes.id == sugestao_id)
    sugestao = session.exec(query).first()

    if not sugestao:
        return { "success": False }

    sugestao.status = status
    session.add(sugestao)
    session.commit()

    return { "success": True }
    


@app.delete("/sugestoes/{sugestao_id}")
async def delete_sugestao(
    sugestao_id: int,
    session: DBSessionDep
):
    query = select(Sugestoes).where(Sugestoes.id == sugestao_id)
    sugestao = session.exec(query).first()
    
    session.delete(sugestao)
    session.commit()
    