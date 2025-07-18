# app/core/auth.py

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.core.config import get_settings

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="https://authapi.healthsafetytech.com/login")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

class TokenData:
    def __init__(self, user_id: int):
        self.user_id = user_id

def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")  # <- pegar o user_id (int) do token
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return TokenData(user_id=user_id)
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
