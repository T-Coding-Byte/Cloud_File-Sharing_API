from pydantic import BaseModel

class passwordSetup(BaseModel):
    password: str

class loginRequest(BaseModel):
    password: str
    
class PasswordReset(BaseModel):
    reset_key: str
    new_password: str