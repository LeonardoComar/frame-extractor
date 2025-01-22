# app/service/frame_processor_service.py
import os
import ffmpeg
import zipfile
import shutil
from tempfile import TemporaryDirectory
from fastapi import HTTPException
import uuid

def process_video(file, interval):
    try:
        with TemporaryDirectory() as temp_dir:
            video_path = os.path.join(temp_dir, file.filename)
            with open(video_path, "wb") as video_file:
                video_file.write(file.file.read())

            frames_dir = os.path.join(temp_dir, "frames")
            os.makedirs(frames_dir, exist_ok=True)

            output_pattern = os.path.join(frames_dir, "frame_%04d.jpg")
            try:
                (
                    ffmpeg
                    .input(video_path, fflags="+genpts")
                    .filter("select", f"not(mod(t,{interval}))")
                    .output(output_pattern, vsync="vfr", format="image2")
                    .run(capture_stdout=True, capture_stderr=True)
                )
            except ffmpeg.Error as e:
                raise HTTPException(status_code=500, detail=f"FFmpeg error: {e.stderr.decode()}")

            frames = os.listdir(frames_dir)
            if not frames:
                raise HTTPException(status_code=500, detail="No frames were extracted from the video.")

            zip_path = os.path.join(temp_dir, "frames.zip")
            with zipfile.ZipFile(zip_path, "w") as zipf:
                for frame in sorted(frames):
                    zipf.write(os.path.join(frames_dir, frame), arcname=frame)

            # Gerar um nome único para evitar conflito
            final_zip_path = os.path.join("/app", f"frames_{str(uuid.uuid4())}.zip")
            shutil.copy(zip_path, final_zip_path)

            return final_zip_path

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
