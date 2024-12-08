# Base
from fastapi import HTTPException, status

# Database
from database.connection import DBSessionDep
from sqlmodel import Session, select

# Dependencies
from apps.auth.utils import get_password_hash

# Schemas
from database.schemas.users import Pessoa, Role, User

# Exceptions
from sqlalchemy.exc import IntegrityError

class Users():

    def create(*,
        username: str,
        password: str,
        role_id: str | None = 1,
        db: DBSessionDep,
    ) -> User:
        
        hashed_password = get_password_hash(password)
        user = User(username=username, password=hashed_password, role_id = role_id)
        
        try:
            db.add(user)
            db.commit()
            db.refresh(user)
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail = "Nome de usuário em uso",
            )
        
        return user
    

    def deactivate(*,
        user_id: str,
        db: DBSessionDep,
    ) -> bool:
        try:
            user = Users.get_by_id(user_id = user_id, db = db)
        except HTTPException:
            raise

        user.ativo = False
        
        try:
            db.add(user)
            db.commit()
        except:
            raise

        return True

    def delete(*,
        user_id: str,
        db: DBSessionDep
    ) -> bool:
        try:
            user = Users.get_by_id(user_id = user_id, db = db)
        except HTTPException:
            raise

        db.delete(user)
        db.commit()

        return True
        
    def get_by_id(
        user_id: int,
        db: DBSessionDep
    ) -> User:  
        user = db.get(User, user_id)
        
        if user is None:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "Usuário não encontrado!"
            )
        
        return user


    def get_by_username(*,
        username: str,
        db: DBSessionDep
    ) -> User:
        query = select(User).where(User.username == username)
        user = db.exec(query).first()
    
        return user if user is not None else False
    

    def index(*,
        offset: int = 0,
        limit: int = 100,
        db: DBSessionDep
    ) -> list[User | None]:
        query = select(User).offset(offset).limit(limit)
        users = db.exec(query)

        return users
    

    def restore(*,
        user_id: str,
        db: DBSessionDep,
    ) -> User:
        try:
            user = Users.get_by_id(user_id = user_id, db = db)
        except HTTPException:
            raise
        
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
        user_id: str,
        password: str,
        db: DBSessionDep,
    ) -> User:
        try:
            user = Users.get_by_id(user_id = user_id, db = db)
        except HTTPException:
            raise

        hashed_password = get_password_hash(password)
        user.password = hashed_password
        try:
            db.add(user)
            db.commit()
            db.refresh(user)
        except:
            raise

        return user


class Roles():

    def create(
        display_name: str,
        db: DBSessionDep,
    ) -> Role:
        
        role = Role(display_name = display_name)
        
        try:
            db.add(role)
            db.commit()
            db.refresh(role)
        except:
            raise
        
        return role
    

    def delete(*,
        role_id: str,
        db: DBSessionDep
    ) -> bool:
        try:
            role = Roles.get_by_id(role_id)
            db.delete(role)
            db.commit()
        except HTTPException:
            raise

        return True
        
    def get_by_id(*,
        role_id: int,
        db: DBSessionDep
    ) -> Role:  
        role = db.get(Role, role_id)
        
        if role is None:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "Papel não encontrado!"
            )
        
        return role

    def index(*,
        offset: int = 0,
        limit: int = 100,
        db: DBSessionDep
    ) -> list[Role | None]:
        query = select(Role).offset(offset).limit(limit)
        roles = db.exec(query)

        return roles
