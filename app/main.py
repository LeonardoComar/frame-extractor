from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.application_routes import router as api_router
from app.repository.dynamodb_repository import create_users_table, create_admin_user
from app.repository.s3_repository import create_s3_bucket
from app.repository.email_ses_repository import verify_ses_email_identity 

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_users_table()
    create_admin_user()
    create_s3_bucket()
    verify_ses_email_identity()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(api_router, prefix="/api")
