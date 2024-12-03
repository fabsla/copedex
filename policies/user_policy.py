from database.schemas.auth import User, RoleName

def before(current_user: User, policy_name: str):
	if current_user.has_role(RoleName.admin):
		return True
	return None

def store(current_user: User):
	return current_user.has_role(RoleName.admin)

def update(current_user: User, object_user: User | None = None):
	if object_user is not None:
		return current_user.id == object_user.id
	return False

def delete(current_user: User, object_user: User | None = None):
	if object_user is not None:
		return current_user.id == object_user.id
	return False

def read_any(current_user: User | None):
	return True

def read(current_user: User | None, object_user: User | None):
	return True