# app/api/frame_routes.py
from fastapi import APIRouter, UploadFile, Form, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.service.frame_processor_service import process_video
from app.core.auth import get_current_user

router = APIRouter()

@router.post("/process-video")
async def process_video_route(
    file: UploadFile,
    interval: int = Form(...),
    current_user: dict = Depends(get_current_user),
):
    try:
        username = current_user.get("sub", "anonymous")
        s3_url = process_video(file, interval, username)
        return JSONResponse(
            content={"message": "Arquivo processado e salvo com sucesso!", "file_url": s3_url},
            status_code=200,
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")