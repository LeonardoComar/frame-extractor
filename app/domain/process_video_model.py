from pydantic import BaseModel, ValidationError
from fastapi import UploadFile, File, Form
from typing import Annotated
from fastapi.exceptions import HTTPException

class ProcessVideoInput(BaseModel):
    file: Annotated[UploadFile, File()]
    interval: Annotated[int, Form(..., description="Intervalo entre frames")]

    @classmethod
    def validate_interval_value(cls, interval: int):
        if interval <= 0:
            raise HTTPException(status_code=422, detail="O intervalo deve ser maior que 0")
        return interval

    @classmethod
    def validate_file_extension(cls, file: UploadFile):
        allowed_extensions = {".mp4", ".mov", ".avi"}
        filename = file.filename.lower()
        if not any(filename.endswith(ext) for ext in allowed_extensions):
            raise HTTPException(
                status_code=422,
                detail="Formato de arquivo não suportado. Use MP4, MOV ou AVI."
            )
        return file

    @classmethod
    def validate_file_size(cls, file: UploadFile):
        max_size = 1 * 1024 * 1024 * 1024  # 1GB em bytes
        file_size = file.size
        if file_size > max_size:
            raise HTTPException(
                status_code=422,
                detail="O tamanho do arquivo excede o limite permitido de 1GB."
            )
        return file

    @classmethod
    def as_form(cls, file: UploadFile = File(...), interval: int = Form(...)):
        try:
            cls.validate_file_extension(file)
            cls.validate_interval_value(interval)
            cls.validate_file_size(file)

            return cls(file=file, interval=interval)
        except ValidationError as e:
            raise HTTPException(status_code=422, detail=e.errors())