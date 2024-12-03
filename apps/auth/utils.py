# Base
from typing import Annotated
from config import settings

from fastapi import Depends, HTTPException, status
from database.connection import get_session, DBSessionDep
# JWT utils
import jwt
from datetime import datetime, timedelta, timezone
from jwt.exceptions import InvalidTokenError

import bcrypt

# Database
from sqlmodel import select, Session

# Schemas
from database.schemas.auth import User, TokenData

# Dependencies
from .dependencies import oauth2_scheme

'''
''  Password Hash
'''
def verify_password(plain_password, hashed_password):
    password_byte_enc = plain_password.encode('utf-8')
    hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password = password_byte_enc , hashed_password = hashed_password)

def get_password_hash(password):
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password
    # Postgres
    # string_password = hashed_password.decode('utf8')
    # return string_password

'''
''  Authentication
'''
def authenticate_user(
    username: str,
    password: str,
    db: Session
):    
    user = get_user_by_username(username = username, db = db)
    
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    
    return user

'''
''  Access Token
'''
def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
):
    to_encode = data.copy()
    expiration_datetime = datetime.now(timezone.utc) + ( expires_delta if expires_delta else timedelta(minutes = 15) )
    to_encode.update({'exp': expiration_datetime})

    encoded_jwt = jwt.encode(to_encode, settings.auth.SECRET_KEY, algorithm = settings.auth.ALGORITHM)

    return encoded_jwt


def get_access_token(user):
    access_token_expires = timedelta(minutes = settings.auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data = {"sub": user.username }, expires_delta = access_token_expires
    )
    return access_token
'''
''  Get Users
'''
def get_user_by_username(
    username: str,
    db: Session
) -> User:
    query = select(User).where(User.username == username)
    user = db.exec(query).first()

    return user if user is not None else False
    
def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: DBSessionDep
)-> User:
    credentials_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = 'Credenciais não podem ser validadas',
        headers = {"WWW-Authenticate": "Bearer"}
    )
 
    try:
        payload = jwt.decode(token, settings.auth.SECRET_KEY, algorithms = [settings.auth.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    
        token_data = TokenData(username = username)
 
    except InvalidTokenError:
        raise credentials_exception
    
    user = get_user_by_username(username = token_data.username, db = db)
    if not user:
        raise credentials_exception
    
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not current_user.ativo:
        raise HTTPException(status_code=400, detail="Usuário inativo")
    
    return current_user