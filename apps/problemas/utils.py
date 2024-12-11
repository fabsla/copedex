# Base
from typing import Annotated
from fastapi import HTTPException, status

# Database
from database.connection import DBSessionDep
from database.utils import upsert_row, delete_row
from sqlmodel import select

# Dependencies
from apps.problemas.dependencies import ProblemaDep

# Schemas
from database.schemas.problemas import Problema, Evento, Tag
from database.schemas.users import User
from apps.problemas.models.requests import EventoRead, ProblemaRead, ProblemaUpdate, TagRead

class Problemas:

    def create(*
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
            upsert_row(model = Problema, model_instance = problema, db = db)
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

    def update(*,
        problema: ProblemaDep,
        problema_update: ProblemaUpdate | None = None,
        evento_update: EventoRead | None = None,
        tags: list[TagRead] | None = None,
        db: DBSessionDep,
    ):
        # if problema_update is not None:
        #     if problema_update.titulo:
        #         problema.titulo = problema_update.titulo
        #     if problema_update.enunciado:
        #         problema.enunciado = problema_update.enunciado
        #     if problema_update.autor:
        #         problema.autor = problema_update.autor
        #     if problema_update.dificuldade:
        #         problema.dificuldade = problema_update.dificuldade
        #     if problema_update.limite_tempo:
        #         problema.limite_tempo = problema_update.limite_tempo
        #     if problema_update.limite_memoria_mb:
        #         problema.limite_memoria_mb = problema_update.limite_memoria_mb

        for attr in dir(problema):
            if not attr.startswith('_') and not callable(getattr(problema, attr)):
                if getattr(problema, attr) != getattr(problema_update, attr):
                    setattr(problema, attr, getattr(problema_update, attr))

        if evento_update is not None:
            evento = db.get(Evento, evento_update.id)
            if evento is not None:
                problema.evento = evento
        
        if tags is not None:
            tags_query = select(Tag).where(tag.id == Tag.id for tag in tags)
            tags = db.exec(tags_query).all()
            if evento is not None:
                problema.tags = tags
        
        try:
            problema_updated = upsert_row(model_instance = problema, db = db)
        except:
            raise

        return problema_updated