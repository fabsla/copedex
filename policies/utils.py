import sys

from typing import Annotated
from fastapi import Depends, status, HTTPException

from apps.auth.utils import get_current_active_user
from database.schemas.users import User

from policies import user_policy, role_policy, problema_policy
    
def _inspect_permission(
    model: str,
    ability: str,
    user: User,
    **kwargs
) -> bool:
    class_name = model + '_policy'
    policy_class = getattr(sys.modules['policies'], class_name)

    if hasattr(policy_class, 'before'):
        before = policy_class.before(user, ability)
        if before is not None:
            return before
    
    ability_check = getattr(policy_class, ability)
    return ability_check(current_user = user, **kwargs)

def check_permissions(
    model: str,
    ability: str,
    user: User,
    **kwargs
):
    permission = _inspect_permission(model = model, ability = ability, user = user, **kwargs)
    if not permission:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail="Você não possui permissão para executar esta ação!"
        )

class Authorizer:
    def __init__(self, model: str, ability: str):
        self.model = model
        self.ability = ability
    
    def __call__(self, current_user: Annotated[User, Depends(get_current_active_user)]):
        check_permissions(model = self.model, ability = self.ability, user = current_user)
        return True    