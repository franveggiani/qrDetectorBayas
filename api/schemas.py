from pydantic import BaseModel
from typing import Optional

class ProcesarVideoRequest(BaseModel):
    video_path: str
    salida_csv: str 
    output_path: str
    output_video: str
    log_path: str
    num_processes: int = 4
    generar_video: bool = True
    modo: str = "hibrido"
    prefijo: str = ""
    factor_lentitud: float = 0.5
