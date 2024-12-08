import sys

from typing import Annotated
from fastapi import Depends, status, HTTPException, Request
from sqlmodel import SQLModel
from apps.auth.utils import get_current_active_user
from database.schemas.users import User
from policies import user_policy, role_policy, problema_policy
     
class Authorizer:
    def __init__(self, model: str, ability: str):
        self.model = model
        self.ability = ability
    
    def __call__(self, current_user: Annotated[User, Depends(get_current_active_user)]):
        permission = inspect_permission(model = self.model, ability = self.ability, user = current_user)
        if not permission:
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Você não possui permissão para executar esta ação!"
            )
        return True    
    
def inspect_permission(
        model: str,
        ability: str,
        user: User,
        **kwargs
    ) -> bool:
	class_name = model + '_policy'
	policy_class = getattr(sys.modules['policies'], class_name)
	
	before = policy_class.before(user, ability)
	return before if before is not None else getattr(policy_class, ability)(user, **kwargs)