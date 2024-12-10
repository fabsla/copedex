# Base
from fastapi import HTTPException, status
from typing import Callable

# Database
from .connection import DBSessionDep
from sqlmodel import SQLModel, select

# Exceptions
from sqlalchemy.exc import IntegrityError

def create_row(
    model_instance: SQLModel,
    db: DBSessionDep
) -> SQLModel:
    try:
        db.add(model_instance)
        db.commit()
        db.refresh(model_instance)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail = "Nome de usuário em uso",
        )
    except:
        raise
    
    return model_instance

def delete_row(*,
    model_instance: SQLModel,
    db: DBSessionDep
) -> bool:
    try:
        db.delete(model_instance)
        db.commit()
    except HTTPException:
        raise

    return True

def get_index(*,
        model: Callable,
        skip: int = 0,
        limit: int = 100,
        db: DBSessionDep,
)-> list[SQLModel | None]:
    query = select(model).offset(skip).limit(limit)
    model_data = db.exec(query)

    return model_data

def get_by_id(*,
    model: Callable,
    id: int,
    db: DBSessionDep
) -> SQLModel:
    model_instance = db.get(model, id)

    if model_instance is None:
        raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = f"{model} não encontrado!"
            )
        
    return model_instance

class ModelGetter:
    def __init__(self, model: Callable):
        self.model = model
    
    def __call__(self, id: int, db: DBSessionDep):
        return get_by_id(model = self.model, id = id, db = db)