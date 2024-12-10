# Base
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

# Database
from database.connection import DBSessionDep
from sqlmodel import select

# Dependencies
from apps.auth.utils import get_password_hash
from database.utils import create_row

# Schemas
from database.schemas.users import Pessoa, Role, User, RoleEnum
from apps.users.models.requests import UserCreate, RoleOptions

# Exceptions
from sqlalchemy.exc import IntegrityError

class Users:

    def create_user(*,
        user_data: UserCreate | OAuth2PasswordRequestForm,
        role: RoleOptions = RoleOptions.leitor,
        db: DBSessionDep,
    ):
        role_name = getattr(RoleEnum, role.name)
        
        hashed_password = get_password_hash(user_data.password)
        user_data = User(username=user_data.username, password=hashed_password, role_id = role_name.value)

        try:
            user = create_row(model_instance = user_data, db = db)
        except IntegrityError:
            raise HTTPException(
                status_code = status.HTTP_409_CONFLICT,
                detail="Nome de usuário indisponível!"
            )

        return user


    def deactivate(*,
        user: User,
        db: DBSessionDep,
    ) -> bool:
        user.ativo = False
        try:
            db.add(user)
            db.commit()
        except:
            raise

        return True

    def get_by_username(*,
        username: str,
        db: DBSessionDep
    ) -> User:
        query = select(User).where(User.username == username)
        user = db.exec(query).first()

        if user is None:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )

        return user
        

    def restore(*,
        user: User,
        db: DBSessionDep,
    ) -> User:    
        if user.ativo:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail = "Usuário já se encontra ativo"
            )
        
        user.ativo = True

        try:
            db.add(user)
            db.commit()
            db.refresh(user)
        except:
            raise

        return user

    
    def update_password(
        user: User,
        password: str,
        db: DBSessionDep,
    ) -> User:
        hashed_password = get_password_hash(password)
        user.password = hashed_password
        try:
            db.add(user)
            db.commit()
            db.refresh(user)
        except:
            raise

        return user