from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from auth import verify_api_key, verify_jwt, create_jwt
import os
from dotenv import load_dotenv

load_dotenv("../.env")

app = FastAPI()

class LoginRequest(BaseModel):
    username: str
    password: str

class ChatRequest(BaseModel):
    prompt: str

@app.post("/login")
def login(data: LoginRequest):
    if data.username == "admin" and data.password == "pass123":
        token = create_jwt(data.username)
        return {"access_token": token}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/chat")
def chat(
    data: ChatRequest,
    api_key: str = Depends(verify_api_key),
    user: str = Depends(verify_jwt)
):
    # PURE LOCAL BACKEND — NO HF, NO API CALLS
    fake_response = f"[LOCAL LLM] Response to: {data.prompt}"

    return {
        "user": user,
        "prompt": data.prompt,
        "response": fake_response,
        "backend": "local-fallback",
        "note": "HF disabled. Real LLM can be plugged later."
    }

