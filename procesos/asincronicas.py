from clases.user import Cliente
from controller.handle_db import HandleDB
import logging,os,traceback
from datetime import datetime

carpeta_logs = 'logs'
if not os.path.exists(carpeta_logs):
    os.makedirs(carpeta_logs)
    
ruta_archivo_log = os.path.join(carpeta_logs, f"log_actualizacion{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
logging.basicConfig(filename=ruta_archivo_log, level=logging.INFO)  

async def actualizacion():
        
    try:
        check = HandleDB()
        clientes = check.verificar_clientes()
        check.__del__()
        for cli in range(1,clientes):

            client = Cliente(cli)
            client.pendientes_entrega()
            for i in client.ordPendientes:
                client.orden = i
                client.obtener_orden()
                client.actualizar_orden()
            client.__del__()
        
        return 200
    except Exception as e:
                logging.error(f"Error HandleDB / verificar_orden: {e} \n {traceback.format_exc()}")
                raise  

async def carga_inicial():
    try:
        check = HandleDB()
        clientes = check.verificar_clientes()
        check.__del__()
        for cli in range(1,clientes):
            client = Cliente(cli)
            if not client.verCargaInicial:
                client.listar()
                client.crear_dfs()
                client.cargar_info()           
            client.__del__()
        return 200
    except Exception as e:
                logging.error(f"Error HandleDB / verificar_orden: {e} \n {traceback.format_exc()}")
                raise  

    
    
