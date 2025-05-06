# Base
from typing import Annotated, Tuple
from fastapi import HTTPException, status

# Database
from database.connection import DBSessionDep
from database.utils import upsert_row, delete_row
from sqlmodel import select, col

# Dependencies
from apps.problemas.dependencies import ProblemaDep, EventoDep, TagDep

# Schemas
from database.schemas.problemas import Problema, Problema_Tag, Evento, Tag, Sugestao, Sugestao_User, Status_Sugestao
from database.schemas.users import User
from apps.problemas.models.requests import EventoCreate, EventoRead, ProblemaCreate, ProblemaRead, ProblemaUpdate, TagRead, SugestaoCreate, SugestaoRead

class Problemas:

    def atribuir_tags(*,
        problema: ProblemaDep,
        tags: list[TagRead] | None = None,
        db: DBSessionDep
    ) -> Tuple[list[Tag], list[TagRead]]:

        tags_inseridas = []
        tags_nao_encontradas = []
        
        for tag in tags:
            tag_lookup = db.get(Tag, tag.id)

            if tag is None:
                tags_nao_encontradas.append(tag)
                continue

            problema.tags.append(tag_lookup)
            tags_inseridas.append(tag_lookup)
        
        try:
            problema = upsert_row(model_instance = problema, db = db)
        except:
            raise

        return tags_inseridas, tags_nao_encontradas


    def create(*,
        problema: ProblemaCreate,
        evento: EventoRead | None = None,
        tags: list[TagRead] | None = None,
        current_user: User,
        db: DBSessionDep,
    ) -> Problema:
        
        problema = Problema(**problema.model_dump())

        if evento is not None:
            evento_results = db.get(Evento, evento.id)
            if evento_results is None:
                evento_db = Evento(**evento.model_dump())
                evento_results = upsert_row(model_instance = evento_db, db = db)
            
            problema.evento = evento_results
                

        if tags is not None:
            tag_query = select(Tag).where(Tag.nome.in_([tag.nome for tag in tags]))
            tag_results = db.exec(tag_query)
            if tag_results is not None:
                problema.tags = [tag for tag in tag_results]

        problema.uploaders.append(current_user)
        
        try:
            problema_updated = upsert_row(model_instance = problema, db = db)
        except:
            raise

        return problema_updated
    
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
            query = query.join(Evento).where(Evento.titulo.in_(eventos))
        
        if tags is not None:
            query = query.join(Problema_Tag).join(Tag).where(
                Tag.nome.in_(tags)
            )

        query = query.limit(limit).offset(skip)

        try:
            problemas = db.exec(query)
        except:
            raise
        
        return problemas if problemas else False

    def update(*,
        problema: Problema,
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
            if not attr.startswith('_') and not callable(getattr(problema, attr)) and getattr(problema_update, attr) is not None:
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
    
class Eventos:

    def get(*,
        evento: EventoRead | None = None,
        skip: int = 0,
        limit: int = 100,
        db: DBSessionDep,      
    ) -> Evento:
        
        query = select(Evento)
        if evento is not None:
            if evento.titulo:
                query = query.where(Evento.titulo == evento.titulo)

        query = query.limit(limit).offset(skip)
        try:
            evento_results = db.exec(query)
        except:
            raise

        return evento_results
    
    def update(*,
        evento: EventoDep,
        evento_update: EventoCreate | None = None,
        db: DBSessionDep,
    ):
        for attr in dir(evento):
            if not attr.startswith('_') and not callable(getattr(evento, attr)) and getattr(evento_update, attr) is not None:
                if getattr(evento, attr) != getattr(evento_update, attr):
                    setattr(evento, attr, getattr(evento_update, attr))
        
        try:
            evento_updated = upsert_row(model_instance = evento, db = db)
        except:
            raise

        return evento_updated

class Tags:

    def get(*,
        tag: TagRead | None = None,
        skip: int = 0,
        limit: int = 100,
        db: DBSessionDep,      
    ) -> Tag:
        
        query = select(Tag)
        if tag is not None:
            if tag.nome:
                query = query.where(Tag.nome == tag.nome)

        query = query.limit(limit).offset(skip)
        try:
            tag_results = db.exec(query)
        except:
            raise

        return tag_results

class Sugestoes:

    def create(*,
        sugestao: SugestaoCreate,
        problema: Problema,
        db: DBSessionDep,
    ) -> Sugestao:
        
        sugestao = Sugestao(**sugestao.model_dump())
        sugestao.problema.append(problema)

        try:
            sugestao_updated = upsert_row(model_instance = sugestao, db = db)
        except:
            raise

        return sugestao_updated
    
    def get(*,
        sugestao: SugestaoRead | None = None,
        skip: int = 0,
        limit: int = 100,
        db: DBSessionDep
    ) -> list[Sugestao]:

        query = select(Sugestao)
        if sugestao is not None:
            if sugestao.descricao:
                query = query.where(
                    Sugestao.descricao == '%'+sugestao.descricao+'%'
                )
            if sugestao.status:
                query = query.where(
                    Sugestao.status == sugestao.status.value
                )
            if sugestao.upvotes_limite_inf:
                query = query.where(
                    Sugestao.upvotes_count() >= sugestao.upvotes_limite_inf
                )
            if sugestao.upvotes_limite_sup:
                query = query.where(
                    Sugestao.upvotes_count() <= sugestao.upvotes_limite_sup
                )
            if sugestao.downvotes_limite_inf:
                query = query.where(
                    Sugestao.downvotes_count() >= sugestao.downvotes_limite_inf
                )
            if sugestao.downvotes_limite_sup:
                query = query.where(
                    Sugestao.downvotes_count() <= sugestao.downvotes_limite_sup
                )

        query = query.limit(limit).offset(skip)

        try:
            sugestoes_results = db.exec(query)
        except:
            raise
        
        return sugestoes_results if sugestoes_results else False

    def votar(*,
        sugestao: Sugestao,
        voto: bool,
        user: User,
        db: DBSessionDep,
    ) -> Sugestao:
            
        voto_link = Sugestao_User(
            sugestao = sugestao,
            user = user,
            voto = voto
        )

        try:
            sugestao_user = upsert_row(model_instance = voto_link, db = db)
            sugestao.votantes.append(sugestao_user)
            
            sugestao_result = upsert_row(model_instance = sugestao, db = db)
        except:
            raise

        return sugestao_result
    
    def update_status(*,
        sugestao: Sugestao,
        status: Status_Sugestao,
        db = DBSessionDep,
    ) -> Sugestao:
        
        sugestao.status = status.value
        
        try:
            sugestao_result = upsert_row(model_instance = sugestao, db = db)
        except:
            raise

        return sugestao_result