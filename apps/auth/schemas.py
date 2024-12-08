from pydantic import BaseModel, SecretStr

class PasswordForm(BaseModel):
    old_password: SecretStr
    new_password: SecretStr
    confirm_password: SecretStr
