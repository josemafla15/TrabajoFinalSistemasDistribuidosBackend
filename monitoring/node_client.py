#!/usr/bin/env python3
"""
Cliente de monitoreo para nodos/VMs
Este script debe ejecutarse en cada VM para enviar heartbeats al servidor Django.
"""
import requests
import json
import time
import socket
import platform
import os
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('node_monitor.log')
    ]
)
logger = logging.getLogger('node_monitor')

# Configuración
SERVER_URL = "http://tu-servidor-django.com/monitoring/nodes/heartbeat/"  # Cambiar a tu URL real
HEARTBEAT_INTERVAL = 60  # segundos
NODE_NAME = socket.gethostname()  # Usar hostname como nombre del nodo

# Intentar importar psutil para métricas avanzadas
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    logger.warning("psutil no está instalado. Las métricas de sistema serán limitadas.")
    HAS_PSUTIL = False

def get_ip_address():
    """Obtiene la dirección IP del nodo"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # No importa si esta dirección es alcanzable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def get_system_metrics():
    """Recopila métricas del sistema"""
    metrics = {
        'system_info': {
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'hostname': socket.gethostname(),
            'processor': platform.processor(),
        }
    }
    
    # Añadir métricas avanzadas si psutil está disponible
    if HAS_PSUTIL:
        metrics.update({
            'cpu': psutil.cpu_percent(interval=1),
            'memory': psutil.virtual_memory().percent,
            'disk': psutil.disk_usage('/').percent,
        })
        metrics['system_info']['ram'] = f"{round(psutil.virtual_memory().total / (1024.0 **3))} GB"
    
    return metrics

def send_heartbeat():
    """Envía heartbeat al servidor Django"""
    try:
        ip_address = get_ip_address()
        metrics = get_system_metrics()
        
        payload = {
            'ip_address': ip_address,
            'name': NODE_NAME,
            'metrics': metrics
        }
        
        logger.info(f"Enviando heartbeat a {SERVER_URL}")
        response = requests.post(
            SERVER_URL,
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            logger.info(f"Heartbeat enviado correctamente: {response.json()}")
        else:
            logger.error(f"Error al enviar heartbeat: {response.status_code} - {response.text}")
            
    except Exception as e:
        logger.error(f"Error al enviar heartbeat: {str(e)}")

def main():
    """Función principal que envía heartbeats periódicamente"""
    logger.info(f"Iniciando cliente de monitoreo para {NODE_NAME}")
    logger.info(f"IP: {get_ip_address()}")
    logger.info(f"Enviando heartbeats a {SERVER_URL} cada {HEARTBEAT_INTERVAL} segundos")
    
    # Bucle principal
    while True:
        send_heartbeat()
        time.sleep(HEARTBEAT_INTERVAL)

if __name__ == "__main__":
    main()