from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import FileResponse
import ffmpeg
import os
import zipfile
from tempfile import TemporaryDirectory
import shutil

app = FastAPI()

@app.post("/process-video")
async def process_video(
    file: UploadFile = File(...),
    interval: int = Form(...),
):
    if not file.filename.endswith(".mp4"):
        raise HTTPException(status_code=400, detail="Only .mp4 files are supported.")
    
    if interval <= 0:
        raise HTTPException(status_code=400, detail="Interval must be greater than 0.")

    try:
        # Diretório temporário para frames e ZIP
        with TemporaryDirectory() as temp_dir:
            video_path = os.path.join(temp_dir, file.filename)

            # Salvar o vídeo enviado
            with open(video_path, "wb") as video_file:
                video_file.write(await file.read())

            # Diretório para os frames
            frames_dir = os.path.join(temp_dir, "frames")
            os.makedirs(frames_dir, exist_ok=True)

            # Extrair frames usando ffmpeg
            output_pattern = os.path.join(frames_dir, "frame_%04d.jpg")
            (
                ffmpeg
                .input(video_path, fflags="+genpts")
                .filter("select", "not(mod(t,20))")  # Apenas o filtro de seleção
                .output(output_pattern, vsync="vfr", format="image2")  # Saída sem manipulação de timestamps
                .run(capture_stdout=True, capture_stderr=True)
            )

            # Verificar se frames foram criados
            if not os.listdir(frames_dir):
                raise HTTPException(status_code=500, detail="No frames were extracted from the video.")

            # Criar arquivo ZIP dos frames
            zip_path = os.path.join(temp_dir, "frames.zip")
            with zipfile.ZipFile(zip_path, "w") as zipf:
                for frame_file in sorted(os.listdir(frames_dir)):
                    frame_path = os.path.join(frames_dir, frame_file)
                    zipf.write(frame_path, arcname=frame_file)

            # Verificar se o ZIP foi criado
            if not os.path.exists(zip_path):
                raise HTTPException(status_code=500, detail="Failed to create the ZIP file.")

            # Mover o arquivo ZIP para um local fixo
            final_zip_path = os.path.join("/app", "frames.zip")  # Certifique-se que /app é acessível no container
            shutil.copy(zip_path, final_zip_path)

            # Retornar o arquivo ZIP
            return FileResponse(
                final_zip_path,
                filename="frames.zip",
                media_type="application/zip",
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

