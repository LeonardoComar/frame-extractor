# app/api/routes.py
from fastapi import APIRouter, HTTPException, UploadFile, Form
from fastapi.responses import FileResponse
from app.service.frame_processor_service import process_video
from app.domain.models import ProcessVideoInput
import shutil

router = APIRouter()

@router.post("/process-video")
async def process_video_route(
    file: UploadFile,
    interval: int = Form(...),
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
