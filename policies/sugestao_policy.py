from database.schemas.users import User, RoleEnum
from database.schemas.problemas import Sugestao

def before(current_user: User, ability: str):
	if current_user.has_role(RoleEnum.admin):
		return True
	return None

def store(current_user: User):
	return current_user.has_role_or_higher(RoleEnum.leitor)

def update(current_user: User, sugestao: Sugestao | None = None):
	if current_user.has_role_or_higher(RoleEnum.leitor):
		if sugestao is not None:
			return sugestao.autor.id == current_user.id

		return True
	return False

def delete(current_user: User, sugestao: Sugestao | None = None):
	if current_user.has_role_or_higher(RoleEnum.leitor):
		if sugestao is not None:
			return sugestao.autor.id == current_user.id

		return True
	return False

def read_any(current_user: User | None):
	return True

def read(current_user: User | None, sugestao: Sugestao | None = None):
	return True