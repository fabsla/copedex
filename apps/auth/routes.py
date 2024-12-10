# Base
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

# Database
from database.connection import DBSessionDep

# Dependencies
from apps.auth.utils import authenticate_user, get_access_token, DBCurrentUserDep

# Models
from apps.users.utils import Users

# Schemas
from database.schemas.auth import Token
from database.schemas.users import UserBase

from apps.auth.schemas import PasswordForm

# Utils
from apps.auth.utils import get_password_hash

router = APIRouter(
    prefix = '/auth',
    tags = ['auth'],
    responses = { 404: {'description': 'Não encontrado'} },
)

'''
Sign-in
'''
@router.post("/signin")
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

@router.post('/signup')
async def signup(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DBSessionDep
) -> UserBase:

    try:
        user = Users.create_user(user_data = form_data, db = db)
    except:
        raise

    return user

@router.post('/update_password')
async def update_password(
    form_data: PasswordForm,
    current_user: DBCurrentUserDep,
    db: DBSessionDep
) -> dict[str, bool]:

    if not authenticate_user(username = current_user.username, password = form_data.old_password.get_secret_value(), db = db):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "A senha inserida é inválida"
        )
    
    if not form_data.new_password.get_secret_value() == form_data.confirm_password.get_secret_value():
        raise HTTPException(
            status_code =  status.HTTP_412_PRECONDITION_FAILED,
            detail = "Os campos 'nova senha' e 'confirmar senha' não são iguais"
        )

    try:
        user = Users.update_password(
            user = current_user,
            password = form_data.new_password.get_secret_value(),
            db = db
        )
    except:
        raise

    return {'sucesso' : True}