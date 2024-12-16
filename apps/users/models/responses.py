from pydantic import BaseModel
from database.schemas.users import UserBase

class UserRestoreResponse(BaseModel):
    sucesso: bool
    user: UserBase