import jwt
import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if SECRET_KEY is None:
    raise RuntimeError("JWT_SECRET_KEY is not set")
ALGORITHM = "HS256"

#data = {
#   "sub": 1
#    }
def create_access_token(data: dict,expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return encoded_jwt

def verify_access_token(token:str):
    payload = jwt.decode(
    token,
    SECRET_KEY,
    algorithms=[ALGORITHM]
)
   
    return payload

    
    