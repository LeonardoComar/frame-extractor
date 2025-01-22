# app/api/routes.py
from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from fastapi.responses import FileResponse
from app.service.frame_processor_service import process_video
import shutil

router = APIRouter()

@router.get("/test")
async def test_route():
    return {"message": "Requisição recebida com sucesso!"}

@router.post("/process-video")
async def process_video_route(
    file: UploadFile = File(...),
    interval: int = Form(...),
):
    try:
        # Processar o vídeo e criar o arquivo ZIP
        zip_path = process_video(file, interval)

        # Mover o arquivo ZIP para um local fixo
        final_zip_path = "/app/frames.zip"  # Certifique-se que /app é acessível no container
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