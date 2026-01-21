from fastapi import Header, HTTPException, Depends
from jose import jwt
from datetime import datetime, timedelta
from config import JWT_SECRET, JWT_ALGO, JWT_EXP_MINUTES, APP_API_KEY

def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != APP_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

def create_jwt(username: str):
    payload = {
        "sub": username,
        "exp": datetime.utcnow() + timedelta(minutes=JWT_EXP_MINUTES)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)
    return token

def verify_jwt(token: str = Header(...)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        return payload["sub"]
    except:
        raise HTTPException(status_code=401, detail="Invalid or Expired Token")

