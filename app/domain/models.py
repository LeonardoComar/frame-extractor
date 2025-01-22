from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, LargeBinary
from pydantic import BaseModel
from typing import Optional

Base = declarative_base()

class UserFile(Base):
    __tablename__ = "users_files"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(255), nullable=False)
    file_zip = Column(LargeBinary, nullable=False)

class UserFileSchema(BaseModel):
    id: Optional[int] = None
    file_name: str
    file_zip: bytes

    class Config:
        from_attributes = True  # Substitui orm_mode
