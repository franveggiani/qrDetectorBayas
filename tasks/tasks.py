from src.utils import generar_csv, generar_video_con_qr
from src.reporting import generar_informe, generar_grafico_distribucion, generar_grafico_temporal
from tasks.hybrid_processing_tasks import procesar_video_parallel

from celery import Celery, shared_task, group

import os
import subprocess

NUM_WORKERS = 1

app = Celery('qrDetector', 
             broker='redis://redis:6379/0', 
             backend='redis://redis:6379/1',
             worker_concurrency=NUM_WORKERS, 
             queue='qr_detector_queue')

# EP01 - PROCESAR VIDEO
@app.task
def qr_detector(input_folder, output_folder, video_name, modo:str='hibrido', log_file_name:str='qr_detector_log', num_processes:int=4, prefijo:str=None, qr_det_csv:str='qr_detections.csv', generar_video: bool=True, factor_lentitud:float=0.5):
    try:
        video_path = os.path.join(input_folder, video_name)
        log_file_path = os.path.join(output_folder, log_file_name)
        qr_detections_path = os.path.join(output_folder, qr_det_csv)
        qr_temporal_file = os.path.join(output_folder, 'qr_temporal_graph.png')
        qr_distribution_file = os.path.join(output_folder, 'qr_temporal_dist.png')
        output_video_file = os.path.join(output_folder, 'qr_detections_video.mp4')
        
        # Procesar el video y generar CSV
        # Ahora se ejecutan tareas, por eso se usa delay. Esto se para conservar el paralelismo con celery.
        if modo:
            datos = procesar_video_parallel(video_path, log_file_path, output_folder, num_processes)
        else:
            raise ValueError("Modo de procesamiento no válido")
        
        generar_csv(datos, prefijo, qr_detections_path)
        generar_informe(datos)
        generar_grafico_temporal(datos, qr_temporal_file)
        generar_grafico_distribucion(datos, qr_distribution_file)
        
        if generar_video:
            print("Generando el video con los recuadros de los códigos QR detectados...")
            generar_video_con_qr(video_path, datos, output_video_file, factor_lentitud)
            
        detalles = {
            "qr_detections_path": qr_detections_path,
            "qr_temporal_file": qr_temporal_file,
            "qr_distribution_file": qr_distribution_file,
            "output_folder": output_video_file if generar_video else "no generado"
        }
        
        return detalles
        
    except subprocess.CalledProcessError as e:
        
        detalles = {
            "error": "error con QR Detector",
            "command": e.args,
            "exit_code": e.returncode, 
            "stdout": e.stdout,
            "stderr": e.stderr
        }
        
        return detalles
    