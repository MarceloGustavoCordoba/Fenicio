from datetime import datetime
import time, os, logging, traceback,psycopg2,json
from sqlalchemy import create_engine

carpeta_logs = 'logs'
if not os.path.exists(carpeta_logs):
    os.makedirs(carpeta_logs)
    
ruta_archivo_log = os.path.join(carpeta_logs, f"log_controller{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
logging.basicConfig(filename=ruta_archivo_log, level=logging.INFO)     

def conexion():
    try:
        with open('db.json', 'r') as archivo_json:
            conn_str = json.load(archivo_json)
            conn_str=conn_str['conn_str']
            logging.info(f"Conexion abierta por archivo.")

    except FileNotFoundError:
        conn_str = os.getenv("DATABASE_URL")
        logging.info(f"Conexion abierta por entorno.")
    return conn_str

class HandleDB():
    def __init__(self):
        conn_str = conexion()
        self._con = psycopg2.connect(conn_str)
        self._cur = self._con.cursor()
        self._engine = create_engine(conn_str)
        
    def verificar_orden(self,idOrden):
        try:
            self._cur.execute(f"SELECT * FROM fen_ordenes where idOrden  = {idOrden}")
            data = self._cur.fetchone()
            if data == None:
                False
            return True
        except Exception as e:
            logging.error(f"Error HandleDB / verificar_orden: {e} \n {traceback.format_exc()}")
            raise  

    def verificar_clientes(self):
        try:
            self._cur.execute(f"select count(*) from fen_vendedores")
            data = self._cur.fetchone()
            return data[0]
        except Exception as e:
            logging.error(f"Error HandleDB / verificar_orden: {e} \n {traceback.format_exc()}")
            raise 

    def verificar_carga_inicial(self,id):
        try:
            self._cur.execute(f"SELECT carga_inicial FROM fen_vendedores where id  = {id}")
            data = self._cur.fetchone()
            return data[0]
        except Exception as e:
            logging.error(f"Error HandleDB / verificar_carga_inicial: {e} \n {traceback.format_exc()}")
            raise  

    def tienda_cliente(self,idCliente):
        try:
            self._cur.execute(f"select tienda from fen_vendedores where id = {idCliente}")
            data = self._cur.fetchone()
            return data[0]
        except Exception as e:
            logging.error(f"Error HandleDB / tienda_cliente: {e} \n {traceback.format_exc()}")
            raise  
    
    def cargar_tablas(self,ordenes,items,descuentos):
        try:
            with self._engine.connect() as connection: 
                ordenes.to_sql('fen_ordenes', connection, index=False, if_exists='append',method='multi')
                items.to_sql('fen_lineas', connection, index=False, if_exists='append',method='multi')
                descuentos.to_sql('fen_descuentos', connection, index=False, if_exists='append',method='multi')
        except Exception as e:
            self._con.rollback()
            logging.error(f"Error HandleDB / cargar_tablas: {e} \n {traceback.format_exc()}")
            raise
    
    def ordenes_pendientes(self,cliente_id):
        try:
            self._cur.execute(f"SELECT \"numeroOrden\"  FROM fen_ordenes where estado = 'APROBADA' and pago_estado = 'APROBADO' and entrega_estado <> 'ENTREGADO' and vendedor = {cliente_id}")
            data = self._cur.fetchall()
            return data
        except Exception as e:
            logging.error(f"Error HandleDB / ordenes_pendientes: {e} \n {traceback.format_exc()}")
            raise   

    def borrar_orden(self,nro_orden):
        try:
            self._cur.execute(f"DELETE FROM fen_descuentos where \"idOrden\" ='{str(nro_orden)}'")
            self._con.commit()
            
            self._cur.execute(f"DELETE FROM fen_lineas where \"idOrden\" ='{str(nro_orden)}'")
            self._con.commit()
            
            self._cur.execute(f"DELETE FROM fen_ordenes where \"idOrden\" ='{str(nro_orden)}'")
            self._con.commit()
            
        except Exception as e:
            logging.error(f"Error HandleDB / borrar_orden: {e} \n {traceback.format_exc()}")
            raise   

    def __del__(self):
        self._con.close()
        logging.info(f"Conexion cerrada.")