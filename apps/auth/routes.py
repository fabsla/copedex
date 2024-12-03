# Base
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

# Database
from database.connection import DBSessionDep

# Dependencies
from apps.auth.dependencies import oauth2_scheme
from apps.auth.utils import authenticate_user, get_access_token, get_current_active_user

# Models
from apps.auth.models import Users

# Schemas
from database.schemas.auth import Pessoa, Role, RoleBase, User, UserBase, UserCreate, Token, TokenData

# Utils
from policies.utils import Authorizer, inspect_permission

router = APIRouter(
    prefix = '/auth',
    tags = ['auth'],
    responses = { 404: {'description': 'Não encontrado'} },
)

'''
Sign-in
'''
@router.post("/signin", tags=['sign-in'])
async def signin(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DBSessionDep
) -> Token:

    user = authenticate_user(form_data.username, form_data.password, db = db)
    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Usuário ou senha inválido(s)!",
            headers = { "WWW-Authenticate": "Bearer" },
        )
    
    return Token(access_token = get_access_token(user), token_type = 'bearer')

@router.post('/signup', tags=['sign-in'])
async def signup(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DBSessionDep
) -> UserBase:
    try:
        user = Users.create(username = form_data.username, password = form_data.password, db = db)
    except HTTPException:
        raise

    return user

'''
Roles
'''
# @router.get("/papeis", tags=['roles'], dependencies=[Depends(Authorizer('user', 'list'))])
# async def list_papeis(
#     token: Annotated[str, Depends(oauth2_scheme)],
#     session: DBSessionDep,
#     ):
        
#     query = select(Role)
#     papeis = session.exec(query).all()

#     lista = [{'id': papel.id, 'display_name': papel.display_name} for papel in papeis]
#     return lista

@router.post("/papeis/", tags=['roles'],dependencies=[Depends(Authorizer('role', 'store'))])
async def store_papel(
    papel: RoleBase,
    db: DBSessionDep
):
    papel_db = Role(display_name = papel.display_name, id_name = papel.id_name)
    
    db.add(papel_db)
    db.commit()

    return { 'success': True }

'''
Users
'''
@router.post("/users", tags=['users'], dependencies=[Depends(Authorizer('user', 'store'))])
async def store_user(
    user: UserCreate,
    db: DBSessionDep,
) -> UserBase:

    user = Users.create(username = user.username, password = user.password, db = db)
    return user


@router.get("/users/me", tags=['users'])
async def read_user_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> UserBase:
    return current_user

@router.get("/users/{user_id}", tags=['users'], dependencies=[Depends(Authorizer('user', 'read_any'))])
async def read_user(
    user: Annotated[UserBase, Depends(Users.get_by_id)],
    current_user: get_current_active_user
) -> UserBase:
    
    permission = inspect_permission(model = 'user', policy_name = 'read', user = current_user, object_user = user)
    if not permission:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Você não possui permissão para executar esta ação!"
        )

    return user

@router.get("/users", tags=['users'], dependencies=[Depends(Authorizer('user', 'read_any'))])
async def list_users(*,
    skip: int = 0,
    limit: int = 100,
    db: DBSessionDep,
) -> list[UserBase]:

    return Users.index(offset = skip, limit = limit, db = db)

