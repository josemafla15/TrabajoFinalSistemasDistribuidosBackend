#!/usr/bin/env python3
"""
Simulador de múltiples nodos para pruebas locales
Este script simula varios nodos enviando heartbeats a tu servidor Django
"""
import requests
import json
import time
import random
import threading
import argparse

# Configuración por defecto
DEFAULT_SERVER_URL = "http://localhost:8000/monitoring/nodes/heartbeat/"
DEFAULT_NUM_NODES = 3
DEFAULT_HEARTBEAT_INTERVAL = 10  # segundos
# Token de autenticación (puedes generarlo desde Django admin o mediante un comando)
AUTH_TOKEN = "tu_token_aqui"  # Reemplaza con un token válido de tu sistema

class NodeSimulator:
    def __init__(self, server_url, node_id, node_name, ip_base="192.168.1", token=None):
        self.server_url = server_url
        self.node_id = node_id
        self.node_name = node_name
        self.ip_address = f"{ip_base}.{100 + node_id}"
        self.running = True
        self.token = token
        
    def get_system_metrics(self):
        """Genera métricas simuladas del sistema"""
        return {
            'cpu': random.uniform(0, 100),
            'memory': random.uniform(20, 95),
            'disk': random.uniform(10, 90),
            'system_info': {
                'platform': random.choice(['Linux', 'Windows', 'Darwin']),
                'hostname': self.node_name,
                'ram': f"{random.randint(4, 64)} GB"
            }
        }
    
    def send_heartbeat(self):
        """Envía heartbeat al servidor Django"""
        try:
            metrics = self.get_system_metrics()
            
            payload = {
                'ip_address': self.ip_address,
                'name': self.node_name,
                'metrics': metrics
            }
            
            print(f"[Nodo {self.node_id}] Enviando heartbeat a {self.server_url}")
            
            # Usar json.dumps para asegurar que el payload es JSON válido
            json_payload = json.dumps(payload)
            print(f"[Nodo {self.node_id}] Payload: {json_payload[:100]}")
            
            response = requests.post(
                self.server_url,
                data=json_payload,  # Usar el JSON ya convertido
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            )
            
            print(f"[Nodo {self.node_id}] Status code: {response.status_code}")
            
            if response.status_code == 200:
                print(f"[Nodo {self.node_id}] Heartbeat enviado correctamente")
                print(f"[Nodo {self.node_id}] Respuesta: {response.text}")
            else:
                print(f"[Nodo {self.node_id}] Error al enviar heartbeat: {response.status_code}")
                print(f"[Nodo {self.node_id}] Detalles: {response.text[:200]}")
                
        except Exception as e:
            print(f"[Nodo {self.node_id}] Error al enviar heartbeat: {str(e)}")
    
    def run(self, interval):
        """Ejecuta el simulador de nodo"""
        print(f"Iniciando simulador para Nodo {self.node_id} ({self.ip_address})")
        
        while self.running:
            self.send_heartbeat()
            
            # Simular variabilidad en el intervalo
            actual_interval = interval * random.uniform(0.9, 1.1)
            time.sleep(actual_interval)
    
    def stop(self):
        """Detiene el simulador"""
        self.running = False

def main():
    parser = argparse.ArgumentParser(description='Simulador de nodos para monitoreo')
    parser.add_argument('--url', default=DEFAULT_SERVER_URL, help='URL del servidor Django')
    parser.add_argument('--nodes', type=int, default=DEFAULT_NUM_NODES, help='Número de nodos a simular')
    parser.add_argument('--interval', type=int, default=DEFAULT_HEARTBEAT_INTERVAL, help='Intervalo de heartbeat en segundos')
    parser.add_argument('--token', default=AUTH_TOKEN, help='Token de autenticación para el API')
    args = parser.parse_args()
    
    print(f"Iniciando simulador con {args.nodes} nodos")
    print(f"Enviando heartbeats a {args.url} cada ~{args.interval} segundos")
    if args.token:
        print(f"Usando token de autenticación: {args.token[:5]}...")
    else:
        print("No se está usando token de autenticación")
    
    # Crear y ejecutar simuladores de nodos en hilos separados
    simulators = []
    threads = []
    
    try:
        for i in range(args.nodes):
            node_name = f"SimNode-{i+1}"
            simulator = NodeSimulator(args.url, i+1, node_name, token=args.token)
            simulators.append(simulator)
            
            thread = threading.Thread(target=simulator.run, args=(args.interval,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # Mantener el programa principal en ejecución
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nDeteniendo simuladores...")
        for simulator in simulators:
            simulator.stop()
        
        # Esperar a que todos los hilos terminen
        for thread in threads:
            thread.join(timeout=1)
        
        print("Simulación finalizada")

if __name__ == "__main__":
    main()