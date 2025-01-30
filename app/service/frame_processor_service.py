# app/service/frame_processor_service.py
import os
import ffmpeg
import zipfile
import uuid
from tempfile import TemporaryDirectory
from fastapi import HTTPException
from app.service.s3_service import upload_to_s3
from app.core.config import settings

def process_video(file, interval, username):
    try:
        with TemporaryDirectory() as temp_dir:
            # Salvar o vídeo temporariamente
            video_path = os.path.join(temp_dir, file.filename)
            with open(video_path, "wb") as video_file:
                video_file.write(file.file.read())

            # Diretório para armazenar os frames
            frames_dir = os.path.join(temp_dir, "frames")
            os.makedirs(frames_dir, exist_ok=True)

            # Extrair frames com o ffmpeg
            output_pattern = os.path.join(frames_dir, "frame_%04d.jpg")
            (
                ffmpeg
                .input(video_path, fflags="+genpts")
                .filter("select", f"not(mod(t,{interval}))")
                .output(output_pattern, vsync="vfr", format="image2")
                .run(capture_stdout=True, capture_stderr=True)
            )

            # Validar se os frames foram extraídos
            frames = os.listdir(frames_dir)
            if not frames:
                raise HTTPException(status_code=500, detail="Nenhum frame foi extraído do vídeo.")

            # Criar o arquivo .zip com os frames
            zip_filename = f"frames_{str(uuid.uuid4())}.zip"
            zip_path = os.path.join(temp_dir, zip_filename)
            with zipfile.ZipFile(zip_path, "w") as zipf:
                for frame in sorted(frames):
                    zipf.write(os.path.join(frames_dir, frame), arcname=frame)

            # Fazer upload do arquivo .zip para o S3
            # bucket_name = settings.AWS_S3_BUCKET_NAME
            object_key = f"{username}/{zip_filename}"
            file_url = upload_to_s3(zip_path, object_key)

            # Retornar o URL do arquivo salvo
            return file_url
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro: {str(e)}")
