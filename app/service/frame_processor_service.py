import os
import zipfile
from tempfile import TemporaryDirectory
import ffmpeg
from fastapi import UploadFile, HTTPException
from app.repository.user_file_repository import UserFileRepository

class FrameProcessorService:
    def __init__(self, repository: UserFileRepository):
        self.repository = repository

    async def process_video(self, file: UploadFile, interval: int) -> int:
        if not file.filename.endswith(".mp4"):
            raise HTTPException(status_code=400, detail="Only .mp4 files are supported.")

        if interval <= 0:
            raise HTTPException(status_code=400, detail="Interval must be greater than 0.")

        with TemporaryDirectory() as temp_dir:
            video_path = os.path.join(temp_dir, file.filename)

            with open(video_path, "wb") as video_file:
                video_file.write(await file.read())

            frames_dir = os.path.join(temp_dir, "frames")
            os.makedirs(frames_dir, exist_ok=True)

            output_pattern = os.path.join(frames_dir, "frame_%04d.jpg")
            (
                ffmpeg
                .input(video_path, fflags="+genpts")
                .filter("select", f"not(mod(t,{interval}))")
                .output(output_pattern, vsync="vfr", format="image2")
                .run(capture_stdout=True, capture_stderr=True)
            )

            zip_path = os.path.join(temp_dir, "frames.zip")
            with zipfile.ZipFile(zip_path, "w") as zipf:
                for frame_file in sorted(os.listdir(frames_dir)):
                    frame_path = os.path.join(frames_dir, frame_file)
                    zipf.write(frame_path, arcname=frame_file)

            with open(zip_path, "rb") as zipf:
                file_zip = zipf.read()

            user_file = await self.repository.save_file(file_name="frames.zip", file_zip=file_zip)

        return user_file.id
