# app/main.py
from fastapi import FastAPI
from app.api.routes import router as api_router

app = FastAPI()

# Incluir as rotas
app.include_router(api_router, prefix="/api")
