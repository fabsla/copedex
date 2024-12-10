from typing import Annotated
from fastapi import Depends
from database.schemas.users import Problema
from database.utils import ModelGetter

ProblemaDep = Annotated[Problema, Depends(ModelGetter(Problema))]
