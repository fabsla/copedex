from database.schemas.auth import Role
from database.connection import Session, engine
from sqlalchemy.exc import IntegrityError

class RoleSeeder:
    
    def seed_db():    
        admin  = Role(id = 3, display_name = "Administrador")
        editor = Role(id = 2, display_name = "Editor")
        leitor = Role(id = 1, display_name = "Leitor")

        with Session(engine) as db:
            try:
                db.add(admin)
                db.add(editor)
                db.add(leitor)
                db.commit()
            except IntegrityError:
                pass
        

