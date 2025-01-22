from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from app.service.frame_processor_service import FrameProcessorService
from app.repository.user_file_repository import UserFileRepository
from app.core.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post("/process-video")
async def process_video(
    file: UploadFile = File(...),
    interval: int = Form(...),
    session: AsyncSession = Depends(get_session)
):
    repository = UserFileRepository(session)
    service = FrameProcessorService(repository)
    file_id = await service.process_video(file, interval)
    return {"file_id": file_id}

@router.get("/download/{file_id}")
async def download_file(
    file_id: int,
    session: AsyncSession = Depends(get_session)
):
    repository = UserFileRepository(session)
    user_file = await repository.get_file(file_id)
    if not user_file:
        raise HTTPException(status_code=404, detail="File not found.")

    return {
        "file_name": user_file.file_name,
        "content": user_file.file_zip
    }
