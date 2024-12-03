from database.schemas.auth import User, RoleName
from database.schemas.problemas import Problema

def before(current_user: User, policy_name: str):
	if current_user.has_role(RoleName.admin):
		return True
	return None

def store(current_user: User):
	return False

def update(current_user: User, problema: Problema | None = None):
	return False

def delete(current_user: User, problema: Problema | None = None):
	return False

def read_any(current_user: User | None):
	return True

def read(current_user: User | None, problema: Problema | None):
	return True