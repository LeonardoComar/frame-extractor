from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Configurações de Autenticação
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Configurações AWS
    DYNAMODB_ENDPOINT: str
    AWS_S3_BUCKET_NAME: str
    AWS_S3_ENDPOINT: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_DEFAULT_REGION: str
    AWS_S3_PUBLIC_URL: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Cria uma instância das configurações
settings = Settings()