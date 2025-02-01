# app/api/frame_routes.py
from fastapi import APIRouter, UploadFile, Form, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.service.frame_processor_service import process_video
from app.service.s3_service import list_user_frame_archives, delete_s3_file
from app.core.auth import get_current_user
from app.domain.process_video_model import ProcessVideoInput

router = APIRouter()

@router.post("/process-video")
async def process_video_route(
    process_input: ProcessVideoInput = Depends(ProcessVideoInput.as_form),
    current_user: dict = Depends(get_current_user),
):
    try:
        username = current_user.get("sub", "anonymous")
        s3_url = process_video(process_input.file, process_input.interval, username)
        return JSONResponse(
            content={"message": "Arquivo processado e salvo com sucesso!", "file_url": s3_url},
            status_code=200,
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")
    
@router.get("/{username}/list-frame-archives")
async def list_frame_archives_route(
    username: str,
    current_user: dict = Depends(get_current_user)
):
    # Verificar se o usuário logado tem permissão para acessar essa rota
    if username != current_user.get("sub"):
        raise HTTPException(status_code=403, detail="Acesso negado")

    try:
        frame_archives = list_user_frame_archives(username)
        return JSONResponse(
            content={"archives": frame_archives},
            status_code=200,
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.delete("/{username}/delete-frame-archive/{filename}")
async def delete_frame_archive(username: str, filename: str, current_user: dict = Depends(get_current_user)):
    # Verifica se o usuário logado é o mesmo que está tentando deletar
    logged_username = current_user.get("sub")
    if logged_username != username:
        raise HTTPException(status_code=403, detail="Acesso negado: você só pode excluir seus próprios arquivos.")
    
    try:
        # Chama o serviço para deletar o arquivo
        delete_s3_file(f"{username}/{filename}")
        return {"message": f"Arquivo '{filename}' removido com sucesso!"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao tentar remover o arquivo: {str(e)}")