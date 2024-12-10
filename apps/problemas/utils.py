# Base
from typing import Annotated
from fastapi import HTTPException, status

# Database
from database.connection import DBSessionDep
from sqlmodel import select

# Schemas
from database.schemas.problemas import Problema, Evento, Tag
from database.schemas.users import User
from apps.problemas.models.requests import EventoRead, ProblemaRead, TagRead

class Problemas:

    def create(*
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
        problema: ProblemaRead | None = None,
        eventos: list[EventoRead] | None = None,
        tags: list[TagRead] | None = None,
        skip: int = 0,
        limit: int = 100,
        db: DBSessionDep
    ) -> list[Problema]:

        query = select(Problema)
        if problema is not None:
            if problema.titulo:
                query = query.where(
                    Problema.titulo == '%'+problema.titulo+'%'
                )
            if problema.enunciado:
                query = query.where(
                    Problema.enunciado == '%'+problema.enunciado+'%'
                )
            if problema.limite_tempo_inf:
                query = query.where(
                    Problema.limite_tempo >= problema.limite_tempo_inf
                )
            if problema.limite_tempo_sup:
                query = query.where(
                    Problema.limite_tempo <= problema.limite_tempo_sup
                )
            if problema.limite_memoria_inf:
                query = query.where(
                    Problema.limite_memoria >= problema.limite_memoria_inf
                )
            if problema.limite_memoria_sup:
                query = query.where(
                    Problema.limite_memoria <= problema.limite_memoria_sup
                )
            if problema.categoria:
                query = query.where(
                    Problema.categoria == problema.categoria
                )
            if problema.dificuldade:
                query = query.where(
                    Problema.dificuldade == problema.dificuldade
                )
            if problema.autor:
                query = query.where(
                    Problema.autor == problema.autor
                )

        if eventos is not None:
            query = query.where(
                Problema.evento in eventos
            )
        
        if tags is not None:
            query = query.where(
                tag in Problema.tags for tag in tags
            )

        query = query.limit(limit).offset(skip)
        problemas = db.exec(query)
        
        return problemas if problemas else False

    
    