from database.schemas.users import User, RoleEnum

def before(current_user: User, ability: str):
	if current_user.has_role(RoleEnum.admin):
		return True
	return None

def store(current_user: User):
	return current_user.has_role(RoleEnum.admin)

def update(current_user: User, object_user: User | None = None):
	if object_user is not None:
		return current_user.id == object_user.id
	return False

def delete(current_user: User, object_user: User | None = None):
	if object_user is not None:
		return current_user.id == object_user.id
	return False

def force_delete(current_user: User, object_user: User | None = None):
	if object_user is not None:
		return current_user.id == object_user.id
	return False

def restore(current_user: User, object_user: User | None = None):
	if object_user is not None:
		return current_user.id == object_user.id
	return False

def read_any(current_user: User | None):
	return True

def read(current_user: User | None, object_user: User | None):
	return True