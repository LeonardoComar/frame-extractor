from fastapi import FastAPI
from app.api.application_routes import router as api_router
from app.repository.dynamodb_repository import create_users_table

async def lifespan(app: FastAPI):
    # Criar a tabela ao iniciar
    create_users_table()
    yield
    # Você pode colocar código para "limpeza" ou finalização aqui, se necessário

app = FastAPI(lifespan=lifespan)

# Incluir as rotas
app.include_router(api_router, prefix="/api")
