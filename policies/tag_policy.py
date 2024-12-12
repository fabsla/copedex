from database.schemas.users import User, RoleEnum
from database.schemas.problemas import Evento

def before(current_user: User, ability: str):
	if current_user.has_role(RoleEnum.admin):
		return True
	return None

def store(current_user: User):
	return current_user.has_role_or_higher(RoleEnum.editor)

def update(current_user: User, evento: Evento | None = None):
	if current_user.has_role_or_higher(RoleEnum.editor):
		return True
	return False

def delete(current_user: User, evento: Evento | None = None):
	if current_user.has_role_or_higher(RoleEnum.editor):
		return True
	return False

def read_any(current_user: User | None):
	return True

def read(current_user: User | None, evento: Evento | None):
	return True