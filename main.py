from fastapi import FastAPI
from procesos.asincronicas import carga_inicial,actualizacion
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import logging
import os


app = FastAPI()

# Configuracion de logging_________________________________________________________________________________
carpeta_logs = 'logs'
if not os.path.exists(carpeta_logs):
    os.makedirs(carpeta_logs)

ruta_archivo_log = os.path.join(carpeta_logs, f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
logging.basicConfig(filename=ruta_archivo_log, level=logging.ERROR)


@app.on_event("startup")
def iniciar_planificador():
    async def ejecutar_tarea():
        await carga_inicial()
        await actualizacion()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(ejecutar_tarea,CronTrigger(hour=15))
    scheduler.start()
    print("planificador iniciado")

@app.get("/")
def root():
    return "Hola"
 