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
from apps.problemas.models.requests import EventoCreate, EventoRead, ProblemaRead, ProblemaCreate, ProblemaUpdate, TagRead, EventoListQueryParams, ProblemaListQueryParams
from apps.problemas.models.responses import EventoSingleResponse, ProblemaFullResponse

# Utils
from policies.utils import Authorizer, check_permissions
from apps.problemas.utils import Problemas, Eventos, Tags

# Subrouters
from .routers.problemas import problema_router
from .routers.eventos import evento_router
from .routers.tags import tag_router

router = APIRouter()

router.include_router(problema_router)
router.include_router(evento_router)
router.include_router(tag_router)