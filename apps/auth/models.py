# Base
from fastapi import HTTPException, status

# Database
from database.connection import DBSessionDep
from sqlmodel import Session, select

# Dependencies
from apps.auth.utils import get_password_hash

# Schemas
from database.schemas.auth import Pessoa, Role, User

class Users():

    def create(
        username: str,
        password: str,
        db: DBSessionDep,
    ) -> User:
        
        hashed_password = get_password_hash(password)
        user = User(username=username, password=hashed_password)
        
        # adicionar try-catch

        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user
    

    def delete(*,
        self,
        user_id: str,
        db: DBSessionDep
    ) -> bool:
        try:
            user = self.get_by_id(user_id)
        except HTTPException:
            raise

        db.delete(user)
        db.commit()

        return True
        
    def get_by_id(*,
        self,
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
        self,
        user: str,
        db: DBSessionDep
    ) -> User:
        query = select(User).where(User.username == user)
        user = db.exec(query).first()
    
        return user if user is not None else False
    

    def index(*,
        self,
        offset: int = 0,
        limit: int = 100,
        db: DBSessionDep
    ) -> list[User | None]:
        query = select(User).offset(offset).limit(limit)
        users = db.exec(query)

        return users

    
    def update_password(
        self,
        user_id: str,
        password: str,
        db: DBSessionDep,
    ) -> bool:
        try:
            user = self.get_by_id(user_id)
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
    