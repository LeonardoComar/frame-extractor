from pydantic import BaseModel, Field, field_validator, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(..., min_length=8)
    status: str = Field(default='active')
    role: str = Field(default='user_level_1')

    # Validação do campo status
    @field_validator("status")
    @classmethod
    def validate_status(cls, value):
        if value not in {"active", "inactive"}:
            raise ValueError("Status deve ser 'active' ou 'inactive'")
        return value

class User(BaseModel):
    username: str
    email: str
    email_hash: str
    hashed_password: str
    status: str = Field(default='active')
    role: str = Field(default='user_level_1')
    
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

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)