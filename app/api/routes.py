# app/api/routes.py
from fastapi import APIRouter, HTTPException, UploadFile, Form, Depends
from fastapi.responses import FileResponse
from app.service.frame_processor_service import process_video
from app.service.auth_service import AuthService
from app.core.auth import get_current_user
from app.domain.models import ProcessVideoInput, UserCreate, UserLogin
import shutil

router = APIRouter()
auth_service = AuthService()

@router.post("/process-video")
async def process_video_route(
    file: UploadFile,
    interval: int = Form(...),
    current_user: dict = Depends(get_current_user),
):
    try:
        # Validação usando o modelo
        input_data = ProcessVideoInput(file=file, interval=interval)

        # Processar o vídeo
        zip_path = process_video(input_data.file, input_data.interval)

        # Mover o arquivo ZIP para um local fixo
        final_zip_path = "/app/frames.zip"
        shutil.copy(zip_path, final_zip_path)

        # Retornar o arquivo ZIP
        return FileResponse(
            final_zip_path,
            filename="frames.zip",
            media_type="application/zip",
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.post("/register")
async def register_user(user: UserCreate):
    try:
        # Gere o hashed_password e registre o usuário
        auth_service.create_user(user.username, user.password, user.email)
        return {"message": "Usuário registrado com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
async def login_user(user: UserLogin):
    try:
        # Aqui você vai usar o modelo 'user' para passar os dados
        token = auth_service.authenticate_user(user.username, user.password)
        return {"access_token": token, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))