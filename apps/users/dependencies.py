from typing import Annotated
from fastapi import Depends
from database.schemas.users import User
from database.utils import ModelGetter

UserDep = Annotated[User, Depends(ModelGetter(User))]