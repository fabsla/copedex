from typing import Annotated
from fastapi import Depends
from database.schemas.users import UserBase, User
from database.utils import ModelGetter

UserDep = Annotated[User, Depends(ModelGetter(User))]