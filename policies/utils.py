import sys

from typing import Annotated
from fastapi import Depends, status, HTTPException, Request
from sqlmodel import SQLModel
from apps.auth.utils import get_current_active_user
from database.schemas.auth import User
from policies import user_policy
     
class Authorizer:
    def __init__(self, model: str, policy_name: str):
        self.model = model
        self.policy_name = policy_name
    
    def __call__(self, current_user: Annotated[User, Depends(get_current_active_user)]):
        permission = inspect_permission(model = self.model, policy_name = self.policy_name, user = current_user)
        if not permission:
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Você não possui permissão para executar esta ação!"
            )
        return True    
    
def inspect_permission(
        model: str,
        policy_name: str,
        user: User,
        **kwargs
    ) -> bool:
	class_name = model + '_policy'
	policy_class = getattr(sys.modules['policies'], class_name)
	
	before = policy_class.before(user, policy_name)
	return before if before is not None else getattr(policy_class, policy_name)(user, **kwargs)