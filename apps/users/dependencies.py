from typing import Annotated
from fastapi import Depends
from database.schemas.users import UserBase
from apps.users.models import Users

UserDep = Annotated[UserBase, Depends(Users.get_by_id)]