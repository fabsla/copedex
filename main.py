# Main
import uvicorn # para testes

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# DB
from database.connection import init_db, connect_db
from database.seeders.roles import RoleSeeder

# App
from config import settings

# Dependencies

# Models

# Schemas

# Routers
from apps.auth.routes import router as auth_router
from apps.users.routes import router as users_router
from apps.problemas.routes import router as problemas_router

# Utils

# import policies

# Lifespan: linhas antes do 'yield' serão executadas on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
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
app.include_router(users_router)
app.include_router(problemas_router)

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
