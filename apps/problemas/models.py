from typing import Annotated

from fastapi import HTTPException, status

from database.connection import DBSessionDep
from sqlmodel import select

from database.schemas.problemas import Pessoa, Role, Token, TokenData

class Pessoas():

    def create(
        self,
        titulo: str
        enunciado=enunciado,
        limite_tempo=limite_tempo,
        limite_memoria_mb=limite_memoria_mb,
        categoria=categoria,
        dificuldade=dificuldade,
        autor=autor,
        evento=evento,
        , db: DBSessionDep):
        
        problema = Problema(
            titulo=titulo,
            enunciado=enunciado,
            limite_tempo=limite_tempo,
            limite_memoria_mb=limite_memoria_mb,
            categoria=categoria,
            dificuldade=dificuldade,
            autor=autor,
            evento=evento,
        )
        try:
            db.add(problema)
            db.commit()
        except:
            raise HTTPException(
                    status_code = status.HTTP_409_CONFLICT,
                    detail = "Nome de usuário já existe!",
                )
    
    def get(*,
        self,
        user: str,
        method: str = 'username',
        db: DBSessionDep
    ):  
        if method == 'username':
            query = select(User).where(User.username == user)
        elif method == 'id':
            query = select(User).where(User.id == user)

        user = db.exec(query).first()
        
        return user if user else False
    

    def index(self, db: DBSessionDep):
        query = select(User)
        users = db.exec(query)

        return users
    
    