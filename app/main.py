from fastapi import FastAPI
from app.api.routes import router
from app.core.database import engine, Base
from contextlib import asynccontextmanager

# Defina o ciclo de vida da aplicação usando um gerenciador de contexto assíncrono
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicializações ao iniciar a aplicação
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield  # Aguarde a aplicação executar
    finally:
        # Recursos para liberar ao finalizar a aplicação
        await engine.dispose()

# Instancie o aplicativo com o ciclo de vida
app = FastAPI(lifespan=lifespan)

# Inclua as rotas
app.include_router(router)
