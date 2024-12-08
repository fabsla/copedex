from typing import Annotated

from fastapi import HTTPException, status

from database.connection import DBSessionDep
from sqlmodel import select

from database.schemas.problemas import Problema, Evento, Tag
from database.schemas.users import User

class Pessoas():

    def create(*
        self,
        titulo: str,
        enunciado: str,
        limite_tempo: int | None = None,
        limite_memoria_mb: int | None = None,
        categoria: str | None = None,
        dificuldade: str | None = None,
        autor: str | None = None,
        evento_id: int | None = None,
        uploaders: list[User] | None = None,
        db: DBSessionDep,
    ) -> Problema:
        
        problema = Problema(
            titulo=titulo,
            enunciado=enunciado,
            limite_tempo=limite_tempo,
            limite_memoria_mb=limite_memoria_mb,
            categoria=categoria,
            dificuldade=dificuldade,
            autor=autor,
            evento_id=evento_id,
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
    
    