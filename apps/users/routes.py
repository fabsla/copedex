# Base
from typing import Annotated
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status

# Database
from database.connection import DBSessionDep

# Dependencies
from apps.auth.utils import DBCurrentUserDep
from apps.users.dependencies import UserDep

# Models
from apps.users.models import Users, Roles

# Schemas
from database.schemas.users import Pessoa, RoleBase, RoleName, RoleEnum, UserBase, UserCreate
from apps.users.schemas import UserRestoreResponse

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
@router.get("/papeis", tags=['roles'], dependencies=[Depends(Authorizer('role', 'list'))])
async def list_papeis(*,
    skip: int = 0,
    limit: int = 100,
    db: DBSessionDep,
)-> RoleBase:

    return Roles.index(skip = skip, limit = limit, db = db)
    
'''
Users
'''
@router.post("/", dependencies=[Depends(Authorizer('user', 'store'))])
async def store_user(
    user: UserCreate,
    role: RoleName,
    db: DBSessionDep,
) -> UserBase:

    role_name = getattr(RoleEnum, role.name)

    try:
        user = Users.create(username = user.username, password = user.password, role_id = role_name.value, db = db)
    except:
        raise

    return user


@router.get("/me")
async def read_user_me(
    current_user: DBCurrentUserDep,
) -> UserBase:
    return current_user

@router.get("/{user_id}", dependencies=[Depends(Authorizer('user', 'read_any'))])
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

@router.delete("/{user_id}", dependencies=[Depends(Authorizer('user', 'delete'))])
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
            Users.deactivate(user_id = user.id, db = db)
        except:
            raise
    else:
        try:
            Users.delete(user_id = user.id, db = db)
        except:
            raise

    return { "sucesso": True }


@router.post("/restore/{user_id}", dependencies=[Depends(Authorizer('user', 'restore'))])
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
        user = Users.restore(user_id = user.id, db = db)
    except:
        raise

    return {"sucesso": True, "user": user}