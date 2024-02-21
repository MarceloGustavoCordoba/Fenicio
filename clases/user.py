from controller.handle_db import HandleDB
from fenicio import funciones
import requests,json, logging, os, traceback
from pandas import json_normalize
from datetime import datetime, timedelta


carpeta_logs = 'logs'
if not os.path.exists(carpeta_logs):
    os.makedirs(carpeta_logs)
    
ruta_archivo_log = os.path.join(carpeta_logs, f"log_clases{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
logging.basicConfig(filename=ruta_archivo_log, level=logging.INFO)  


class Cliente():
    def __init__(self,id):
        self.db = HandleDB()
        self.idVendedor = id
        self.tienda = self.db.tienda_cliente(self.idVendedor)
        self.verCargaInicial = self.db.verificar_carga_inicial(self.idVendedor)
        self.inicio = (datetime.now() - timedelta(days=366)).strftime('%Y-%m-%d')
        self.fin = (datetime.now()- timedelta(days=1)).strftime('%Y-%m-%d')
        self.pag = 1
        self.orden = 1
        self.lista_ordenes = []

    def query(self):
        self.req_historica = f"{self.tienda}/API_V1/ordenes/?fDesde={self.inicio}&fHasta={self.fin}&tot=500&pag={self.pag}"
        self.req_orden = f"{self.tienda}/API_V1/ordenes/{self.orden}"
    
    def listar(self):
        self.pag = 1
        self.query()
        total = 1
        while total > 0:
            response = requests.get(self.req_historica)
            total = len(json.loads(response.text)['ordenes'])
            if total >0:
                for ord in json.loads(response.text)['ordenes']:
                    self.lista_ordenes.append(ord)
            self.pag += 1
            self.query()
    
    def obtener_orden(self):
        self.query()
        response = requests.get(self.req_orden)
        response = json.loads(response.text)
        for atri in response['orden']['lineas']:
            atri['atributos'] = None
        self.orden_json = response

    def actualizar_orden(self):
        try:
                
            self.lista_ordenes=[]
            self.lista_ordenes.append(self.orden_json['orden'])
            self.crear_dfs()
            self.db.borrar_orden(self.orden)
            self.cargar_info()
        
        except Exception as e:
                    logging.error(f"Error actualizar_orden: {e} \n {traceback.format_exc()}\n{traceback.format_exc()}")
                    raise            

    def crear_dfs(self):
        
        self.tOrdenes = json_normalize(self.lista_ordenes).rename(columns=lambda x: x.replace('.', '_')).drop(columns='lineas')
        self.tLineas = json_normalize(self.lista_ordenes,['lineas'],['idOrden']).rename(columns=lambda x: x.replace('.', '_')).drop(columns='descuentos')
        self.tDescuentos = json_normalize(self.lista_ordenes,['lineas','descuentos'],'idOrden')

        self.tOrdenes['vendedor'] = self.idVendedor
        self.tLineas['vendedor'] = self.idVendedor
        self.tDescuentos['vendedor'] = self.idVendedor

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.tOrdenes['last_update']=current_time
        self.tLineas['last_update']=current_time
        self.tDescuentos['last_update']=current_time

    def cargar_info(self):
        self.db.cargar_tablas(self.tOrdenes,self.tLineas,self.tDescuentos)

    def pendientes_entrega(self):
        self.ordPendientes = []
        lista = self.db.ordenes_pendientes(self.idVendedor)
        if len(lista)>0:
            for i in lista:
                self.ordPendientes.append(i[0])
    
    def __del__(self):
        self.db.__del__()
