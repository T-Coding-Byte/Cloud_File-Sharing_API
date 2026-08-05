from pydantic import BaseModel

class passwordSetup(BaseModel):
    password: str

class loginRequest(BaseModel):
    password: str