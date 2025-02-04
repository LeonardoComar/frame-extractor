from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.application_routes import router as api_router
from app.repository.dynamodb_repository import create_users_table
from app.repository.s3_repository import create_s3_bucket
from app.repository.email_ses_repository import verify_ses_email_identity 

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Criar a tabela ao iniciar
    create_users_table()
    create_s3_bucket()
    verify_ses_email_identity()
    yield
    # Você pode colocar código para "limpeza" ou finalização aqui, se necessário

app = FastAPI(lifespan=lifespan)

# Incluir as rotas
app.include_router(api_router, prefix="/api")
