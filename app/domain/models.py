# app/domain/models.py
from pydantic import BaseModel, Field, field_validator, EmailStr
from fastapi import UploadFile
import os

class ProcessVideoInput(BaseModel):
    file: UploadFile
    interval: int = Field(..., gt=0, description="O intervalo deve ser maior que 0")

    @field_validator("interval")
    def validate_interval(cls, value):
        if value <= 0:
            raise ValueError("Intervalo precisa ser maior que 0")
        return value

    @field_validator("file")
    def validate_file_extension(cls, file: UploadFile):
        # Verifica se o arquivo tem extensão .mp4
        filename = file.filename
        if not filename.lower().endswith(".mp4"):
            raise ValueError("O arquivo deve ser do tipo .mp4")
        return file

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    status: str = Field(default='active')  # Valor padrão para status

    # Validação do campo status
    @field_validator("status")
    @classmethod
    def validate_status(cls, value):
        if value not in {"active", "inactive"}:
            raise ValueError("Status deve ser 'active' ou 'inactive'")
        return value

class User(BaseModel):
    username: str
    email: EmailStr
    hashed_password: str
    status: str = Field(default='active')  # Valor padrão para status

    # Validação do campo status
    @field_validator("status")
    @classmethod
    def validate_status(cls, value):
        if value not in {"active", "inactive"}:
            raise ValueError("Status deve ser 'active' ou 'inactive'")
        return value

class UserLogin(BaseModel):
    username: str
    password: str