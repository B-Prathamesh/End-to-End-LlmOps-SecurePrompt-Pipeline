import os
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
APP_API_KEY = os.getenv("APP_API_KEY")
JWT_SECRET = os.getenv("JWT_SECRET", "supersecret")
JWT_ALGO = "HS256"
JWT_EXP_MINUTES = 60

