# Base
from typing import Annotated, Tuple
from fastapi import HTTPException, status

# Database
from database.connection import DBSessionDep
from database.utils import upsert_row, delete_row
from sqlmodel import select, col

# Dependencies
from apps.problemas.dependencies import ProblemaDep, EventoDep, TagDep
from apps.auth.utils import DBCurrentUserDep

# Schemas
from database.schemas.problemas import Problema, Problema_Tag, Evento, Tag, Sugestao, Sugestao_User, Status_Sugestao
from database.schemas.users import User
from apps.problemas.models.requests import EventoCreate, EventoRead, ProblemaCreate, ProblemaRead, ProblemaUpdate, TagRead, TagCreate, SugestaoCreate, SugestaoRead

class Problemas:

    def atribuir_tags(*,
        problema: ProblemaDep,
        tags: list[TagRead] | None = None,
        db: DBSessionDep
    ) -> Tuple[list[Tag], list[TagRead]]:

        tags_inseridas = []
        tags_erros = []
        tags_atribuidas = [tag.id for tag in problema.tags]
        
        for tag in tags:
            if tag.id in tags_atribuidas:
                tags_erros.append({"Tag": tag, "Erro": "Já atribuída"})
                continue

            tag_lookup = db.get(Tag, tag.id)

            if tag_lookup is None:
                tags_erros.append({"Tag": tag, "Erro": "Não encontrada"})
                continue

            problema.tags.append(tag_lookup)
            tags_inseridas.append(tag_lookup)
        
        try:
            problema = upsert_row(model_instance = problema, db = db)
        except:
            raise

        return tags_inseridas, tags_erros


    def desvincular_tags(*,
        problema: ProblemaDep,
        tags: list[TagRead] | None = None,
        db: DBSessionDep
    ) -> Tuple[list[Tag], list[TagRead]]:

        tags_a_remover = [tag.id for tag in tags]
        tags_atribuidas = problema.tags.copy()

        for tag in tags_atribuidas:
            if tag.id in tags_a_remover:
                problema.tags.remove(tag)
        
        try:
            problema = upsert_row(model_instance = problema, db = db)
        except:
            raise
    

    def create(*,
        problema: ProblemaCreate,
        evento: EventoRead | None = None,
        tags: list[TagRead] | None = None,
        current_user: User,
        db: DBSessionDep,
    ) -> Problema:
        
        problema = Problema(**problema.model_dump())

        if evento is not None:
            evento_db = db.get(Evento, evento.id)
            if evento is not None:
                problema.evento = evento_db
        
        if tags is not None:
            tags_query = select(Tag).where(Tag.id.in_([tag.id for tag in tags]))
            tags_found = db.exec(tags_query).all()
            if tags_found:
                problema.tags = tags_found


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
                query = query.where(Problema.titulo.like('%'+problema.titulo+'%'))

            if problema.enunciado:
                query = query.where(Problema.enunciado.like('%'+problema.enunciado+'%'))

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
        if problema_update is not None:
            if problema_update.titulo:
                problema.titulo = problema_update.titulo

            if problema_update.enunciado:
                problema.enunciado = problema_update.enunciado

            if problema_update.autor:
                problema.autor = problema_update.autor

            if problema_update.dificuldade:
                problema.dificuldade = problema_update.dificuldade
            
            if problema_update.categoria:
                problema.categoria = problema_update.categoria

            if problema_update.limite_tempo:
                problema.limite_tempo = problema_update.limite_tempo
            
            if problema_update.limite_memoria_mb:
                problema.limite_memoria_mb = problema_update.limite_memoria_mb

        if evento_update is not None:
            evento = db.get(Evento, evento_update.id)
            if evento is not None:
                problema.evento = evento
        
        if tags is not None:
            tags_query = select(Tag).where(Tag.id.in_([tag.id for tag in tags]))
            tags_found = db.exec(tags_query).all()
            if tags_found:
                problema.tags = tags_found
        
        try:
            problema_updated = upsert_row(model_instance = problema, db = db)
        except:
            raise

        return problema_updated
    
    def vincular_evento(*,
        problema: ProblemaDep,
        evento: EventoRead,
        db: DBSessionDep
    ) -> Problema:
        
        try:
            evento_db = db.get(Evento, evento.id)
            if evento_db is not None:
                problema.evento = evento_db
        
            problema = upsert_row(model_instance = problema, db = db)
            return problema
        except:
            raise


    def desvincular_evento(*,
        problema: ProblemaDep,
        db: DBSessionDep
    ) -> Problema:
        
        try:
            problema.evento = None

            problema = upsert_row(model_instance = problema, db = db)
        except:
            raise
    
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
                query = query.where(Evento.titulo.like("%"+evento.titulo+"%"))

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
        if evento.titulo != evento_update.titulo:
            evento.titulo = evento_update.titulo
        
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
            if tag.nome is not None:
                query = query.where(Tag.nome.like("%"+tag.nome+"%"))

        query = query.limit(limit).offset(skip)
        try:
            tag_results = db.exec(query)
            return tag_results
        except:
            raise
    
    def update(*,
        tag: TagDep,
        tag_update: TagCreate | None = None,
        db: DBSessionDep,
    ):  
        if tag.nome != tag_update.nome:
            tag.nome = tag_update.nome
        
        try:
            tag_updated = upsert_row(model_instance = tag, db = db)
        except:
            raise

        return tag_updated


class Sugestoes:

    def create(*,
        sugestao: SugestaoCreate,
        problema: Problema,
        current_user: DBCurrentUserDep,
        db: DBSessionDep,
    ) -> Sugestao:
        
        sugestao = Sugestao(**sugestao.model_dump())
        sugestao.problema = problema
        sugestao.autor = current_user
        sugestao.autor_id = current_user.id
        sugestao.ativa = True

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
            if sugestao.problema_id:
                query = query.where(
                    Sugestao.problema_id == sugestao.problema_id
                )
            if sugestao.autor_id:
                query = query.where(
                    Sugestao.autor_id == sugestao.autor_id
                )
            if sugestao.descricao:
                query = query.where(
                    Sugestao.descricao.like('%'+sugestao.descricao+'%')
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
            
        voto_link = Sugestoes.get_voto(sugestao = sugestao, user = user, db = db).one()
        if voto_link is None:
            voto_link = Sugestao_User(
                sugestao = sugestao,
                user = user,
            )

        voto_link.voto = voto

        try:
            sugestao_user = upsert_row(model_instance = voto_link, db = db)
            
            if sugestao_user not in sugestao.votantes:
                sugestao.votantes.append(sugestao_user)
                sugestao = upsert_row(model_instance = sugestao, db = db)

            return sugestao
            
        except:
            raise

    
    def get_voto(*,
        sugestao: Sugestao,
        user: User,
        db: DBSessionDep
    ) -> Sugestao_User:

        query = select(Sugestao_User).where(Sugestao_User.user_id == user.id).where(Sugestao_User.sugestao_id == sugestao.id)

        try:
            sugestao_user = db.exec(query)
            return sugestao_user
        except:
            raise
    
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