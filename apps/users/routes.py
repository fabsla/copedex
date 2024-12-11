# Base
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from pydantic import BaseModel

# Database
from database.connection import DBSessionDep
from database.utils import get_index, upsert_row, get_by_id, delete_row

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
from policies.utils import Authorizer, check_permissions

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

@router.get("/{id}", dependencies=[Depends(Authorizer('user', 'read'))])
async def read_user(
    user: UserDep,
    current_user: DBCurrentUserDep,
) -> UserBase:
    
    check_permissions(model = 'user', ability = 'read', user = current_user, object_user = user)

    return user

@router.get("/", dependencies=[Depends(Authorizer('user', 'read_any'))])
async def list_users(*,
    skip: int = 0,
    limit: int = 100,
    db: DBSessionDep,
) -> list[UserBase]:

    return get_index(model = User, skip = skip, limit = limit, db = db)

@router.delete("/{id}", dependencies=[Depends(Authorizer('user', 'delete'))])
async def delete_user(*,
    user: UserDep,
    current_user: DBCurrentUserDep,
    db: DBSessionDep
) -> dict[str, bool]:
    
    should_force_delete = not user.ativo
    ability = 'delete' if not should_force_delete else 'force_delete'
    
    check_permissions(model = 'user', ability = ability, user = current_user, object_user = user)
    
    try:
        if not should_force_delete:
            Users.deactivate(user = user, db = db)
        else:
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

    check_permissions(model = 'user', ability = 'restore', user = current_user, object_user = user)

    try:
        user = Users.restore(user = user, db = db)
    except:
        raise

    return {"sucesso": True, "user": user}