from database.schemas.users import User, RoleEnum
from database.schemas.problemas import Problema

def before(current_user: User, ability: str):
	if current_user.has_role(RoleEnum.admin):
		return True
	return None

def store(current_user: User):
	return current_user.has_role_or_higher(RoleEnum.editor)

def update(current_user: User, problema: Problema | None = None):
	if current_user.has_role_or_higher(RoleEnum.editor):
		if problema is not None:
			return current_user in problema.uploaders
		
		return True # pode acessar a rota
	return False

def delete(current_user: User, problema: Problema | None = None):
	if current_user.has_role_or_higher(RoleEnum.editor):
		if problema is not None:
			return current_user in problema.uploaders
		
		return True # pode acessar a rota
	return False

def read_any(current_user: User | None):
	return True

def read(current_user: User | None, problema: Problema | None):
	return True