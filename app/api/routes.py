# app/api/routes.py
from fastapi import APIRouter, HTTPException, UploadFile, Form, Depends
from fastapi.responses import FileResponse, JSONResponse
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
        # Obter o username do usuário autenticado
        username = current_user.get("sub", "anonymous")

        # Processar o vídeo e fazer upload para o S3
        s3_url = process_video(file, interval, username)

        # Retornar o URL do arquivo salvo no S3
        return JSONResponse(
            content={"message": "Arquivo processado e salvo com sucesso!", "file_url": s3_url},
            status_code=200,
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
    
@router.get("/users", dependencies=[Depends(get_current_user)])
async def list_users():
    try:
        # Obter a lista de usuários
        users = auth_service.get_all_users()
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
@router.post("/users/{username}/activate", dependencies=[Depends(get_current_user)])
async def activate_user(username: str):
    try:
        # Ativar o usuário
        auth_service.update_user_status(username, "active")
        return {"message": f"Usuário {username} ativado com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
@router.post("/users/{username}/deactivate", dependencies=[Depends(get_current_user)])
async def deactivate_user(username: str):
    try:
        # Inativar o usuário
        auth_service.update_user_status(username, "inactive")
        return {"message": f"Usuário {username} inativado com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")