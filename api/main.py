from fastapi import FastAPI, HTTPException, Path
from .schemas import ProcesarVideoRequest
import subprocess

import sys
import os

print("Python ejecutado:", sys.executable)
print("Directorio actual:", os.getcwd())
print("Archivos en el directorio actual:", os.listdir("."))

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hola carajo"}

# EP01 - PROCESAR VIDEO
@app.post("/qr_detector")
async def procesar_video(params: ProcesarVideoRequest):

    try:
        QR_DETECTOR_PATH = "qrDetector-main/main.py"  # Relativo a la ubicación del script

        #BASE_DIR = Path(__file__).parent.parent.parent
        #QR_DETECTOR_PATH = BASE_DIR / "qrDetector-main" / "main.py"

        command = [
                "python", str(QR_DETECTOR_PATH), 
                "--video-path", str(params.video_path),
                "--salida-csv", str(params.salida_csv), 
                "--log-path", str(params.log_path), 
                "--num-processes", str(params.num_processes),
                "--modo", str(params.modo), 
                "--output-path", str(params.output_path),
                "--factor-lentitud", str(params.factor_lentitud),
                "--prefijo", str(params.prefijo)
                # "--generar-video", 
                # "--output-video", str(params.output_video)
            ]
        
        if params.generar_video:
            command.append("--generar-video")
            command.append("--output-video")
            command.append(str(params.output_video))

        result = subprocess.run(
            command, check=True, capture_output=True, text=True
        )

        detalles = {
            "return_code": result.returncode,
            "stdout": result.stdout,
            "args": result.args
        }
    
    except subprocess.CalledProcessError as e:
        
        detalles = {
            "error": "error con QR Detector",
            "command": e.args,
            "exit_code": e.returncode, 
            "stdout": e.stdout,
            "stderr": e.stderr
        }

        raise HTTPException(status_code=400, detail=detalles)