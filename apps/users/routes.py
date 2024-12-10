# Base
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from pydantic import BaseModel

# Database
from database.connection import DBSessionDep
from database.utils import get_index, create_row, get_by_id, delete_row

# Dependencies
from apps.auth.utils import DBCurrentUserDep, get_password_hash
from apps.users.dependencies import UserDep

# Models
from apps.users.utils import Users

# Schemas
from database.schemas.users import Pessoa, Role, RoleBase, RoleEnum, User, UserBase
from apps.users.models.requests import UserCreate, RoleOptions
from apps.users.models.responses import UserRestoreResponse

# Utils
from policies.utils import Authorizer, inspect_permission

router = APIRouter(
    prefix = '/users',
    tags = ['users'],
    responses = { 404: {'description': 'Não encontrado'} },
)

'''
Roles
'''
@router.get("/papeis", tags=['roles'], dependencies=[Depends(Authorizer('role', 'read_any'))])
async def list_papeis(*,
    skip: int = 0,
    limit: int = 100,
    db: DBSessionDep,
)-> list[RoleBase]:
    return get_index(model = Role, skip = skip, limit = limit, db = db)
    
'''
Users
'''
@router.post("/", dependencies=[Depends(Authorizer('user', 'store'))])
async def store_user(
    user: UserCreate,
    role: RoleOptions,
    db: DBSessionDep,
) -> UserBase:

    try:
        user = Users.create_user(user_data = user, role = role, db = db)
    except:
        raise

    return user


@router.get("/me")
async def read_user_me(
    current_user: DBCurrentUserDep,
) -> UserBase:
    return current_user

@router.get("/{id}", dependencies=[Depends(Authorizer('user', 'read_any'))])
async def read_user(
    user: UserDep,
    current_user: DBCurrentUserDep,
) -> UserBase:
    
    permission = inspect_permission(model = 'user', ability = 'read', user = current_user, object_user = user)
    if not permission:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Você não possui permissão para executar esta ação!"
        )

    return user

@router.get("/", dependencies=[Depends(Authorizer('user', 'read_any'))])
async def list_users(*,
    skip: int = 0,
    limit: int = 100,
    db: DBSessionDep,
) -> list[UserBase]:

    return Users.index(offset = skip, limit = limit, db = db)

@router.delete("/{id}", dependencies=[Depends(Authorizer('user', 'delete'))])
async def delete_user(*,
    user: UserDep,
    current_user: DBCurrentUserDep,
    db: DBSessionDep
) -> dict[str, bool]:
    
    should_force_delete = not user.ativo
    ability = 'delete' if not should_force_delete else 'force_delete'
    
    permission = inspect_permission(model = 'user', ability = ability, user = current_user, object_user = user)
    if not permission:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Você não possui permissão para executar esta ação!"
        )
    
    if not should_force_delete:
        try:
            Users.deactivate(user = user, db = db)
        except:
            raise
    else:
        try:
            delete_row(model_instance = user, db = db)
        except:
            raise

    return { "sucesso": True }


@router.post("/restore/{id}", dependencies=[Depends(Authorizer('user', 'restore'))])
async def restore_user(*,
    user: UserDep,
    current_user: DBCurrentUserDep,
    db: DBSessionDep,
) -> UserRestoreResponse:
    
    permission = inspect_permission(model = 'user', ability = 'restore', user = current_user, object_user = user)
    if not permission:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Você não possui permissão para executar esta ação!"
        )
    
    try:
        user = Users.restore(user = user, db = db)
    except:
        raise

    return {"sucesso": True, "user": user}