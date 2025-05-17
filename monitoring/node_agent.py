#!/usr/bin/env python
"""
Agente de monitoreo para nodos
Este script debe ejecutarse en cada nodo (VM) que deseas monitorear.
Envía heartbeats periódicos al servidor orquestador.

Uso:
python node_agent.py --url http://ip-del-orquestador:8000/monitoring/simple/heartbeat/ --interval 30
"""

import argparse
import json
import logging
import platform
import psutil
import requests
import socket
import time
import uuid
import os
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("node_agent.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NodeAgent:
    def __init__(self, server_url, interval=30, node_name=None):
        self.server_url = server_url
        self.interval = interval
        self.node_id = str(uuid.uuid4())
        
        # Obtener la dirección IP real de la máquina
        self.ip_address = self.get_ip_address()
        
        # Usar el nombre proporcionado o el hostname de la máquina
        self.node_name = node_name or socket.gethostname()
        
        logger.info(f"Agente iniciado para nodo {self.node_name} ({self.ip_address})")
        logger.info(f"Enviando heartbeats a {self.server_url} cada {self.interval} segundos")
    
    def get_ip_address(self):
        """Obtiene la dirección IP real de la máquina"""
        try:
            # Crear una conexión temporal para determinar la IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception as e:
            logger.error(f"Error al obtener IP: {str(e)}")
            return "127.0.0.1"  # Fallback a localhost
    
    def get_system_metrics(self):
        """Obtiene métricas reales del sistema"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memoria
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disco
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Información del sistema
            system_info = {
                "platform": platform.system(),
                "hostname": socket.gethostname(),
                "platform_version": platform.version(),
                "processor": platform.processor(),
                "python_version": platform.python_version(),
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat()
            }
            
            # Procesos
            process_count = len(psutil.pids())
            
            # Información de red
            net_io = psutil.net_io_counters()
            network_info = {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv
            }
            
            return {
                "cpu": cpu_percent,
                "memory": memory_percent,
                "disk": disk_percent,
                "system_info": system_info,
                "process_count": process_count,
                "network": network_info,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error al obtener métricas: {str(e)}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def send_heartbeat(self):
        """Envía heartbeat al servidor orquestador"""
        try:
            metrics = self.get_system_metrics()
            
            payload = {
                "ip_address": self.ip_address,
                "name": self.node_name,
                "metrics": metrics
            }
            
            logger.info(f"Enviando heartbeat a {self.server_url}")
            
            # Usar json.dumps para asegurar que el payload es JSON válido
            json_payload = json.dumps(payload)
            
            response = requests.post(
                self.server_url,
                data=json_payload,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                timeout=10  # Timeout de 10 segundos
            )
            
            if response.status_code == 200:
                logger.info(f"Heartbeat enviado correctamente: {response.status_code}")
                logger.debug(f"Respuesta: {response.text}")
            else:
                logger.error(f"Error al enviar heartbeat: {response.status_code}")
                logger.error(f"Detalles: {response.text[:200]}")
                
        except requests.exceptions.ConnectionError:
            logger.error(f"Error de conexión al enviar heartbeat. Servidor no disponible.")
        except Exception as e:
            logger.error(f"Error al enviar heartbeat: {str(e)}")
    
    def run(self):
        """Ejecuta el agente en un bucle infinito"""
        try:
            while True:
                self.send_heartbeat()
                time.sleep(self.interval)
        except KeyboardInterrupt:
            logger.info("Agente detenido por el usuario")
        except Exception as e:
            logger.error(f"Error en el agente: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Agente de monitoreo para nodos')
    parser.add_argument('--url', required=True, help='URL del servidor orquestador')
    parser.add_argument('--interval', type=int, default=30, help='Intervalo entre heartbeats en segundos')
    parser.add_argument('--name', help='Nombre personalizado para el nodo')
    
    args = parser.parse_args()
    
    agent = NodeAgent(
        server_url=args.url,
        interval=args.interval,
        node_name=args.name
    )
    
    agent.run()

if __name__ == '__main__':
    main()