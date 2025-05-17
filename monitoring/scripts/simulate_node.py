# monitoring/scripts/simulate_node.py
#!/usr/bin/env python
import argparse
import time
import socket
import requests
import threading
import json
import random
import sys
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('node_simulator')

# Estado global para los nodos
nodes = {}

class NodeHTTPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Sobrescribir para evitar logs excesivos
        return
    
    def do_GET(self):
        """Manejar solicitudes GET"""
        if self.path == '/health':
            # Endpoint para verificar el estado del nodo
            node_id = self.server.node_id
            response = {
                "status": "alive",
                "id": node_id,
                "name": nodes[node_id]["name"],
                "last_heartbeat": nodes[node_id]["last_heartbeat_sent"]
            }
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Manejar solicitudes POST"""
        if self.path == '/simulate-failure':
            # Endpoint para simular un fallo
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            node_id = self.server.node_id
            failure_duration = data.get('duration', 180)  # Duración en segundos
            
            nodes[node_id]["simulate_failure"] = True
            logger.info(f"Node {nodes[node_id]['name']} simulating failure for {failure_duration} seconds")
            
            # Programa la recuperación automática después de la duración especificada
            def recover():
                nodes[node_id]["simulate_failure"] = False
                logger.info(f"Node {nodes[node_id]['name']} recovered after {failure_duration} seconds")
            
            threading.Timer(failure_duration, recover).start()
            
            response = {
                "status": "failure_simulated",
                "duration": failure_duration,
                "recovery_at": time.time() + failure_duration
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    """Servidor HTTP con soporte para múltiples hilos"""
    def __init__(self, server_address, RequestHandlerClass, node_id):
        self.node_id = node_id
        super().__init__(server_address, RequestHandlerClass)

def register_with_server(backend_url, name, ip_address, port, node_type):
    """Registra este nodo con el servidor"""
    try:
        response = requests.post(
            f"{backend_url}/monitoring/nodes/register/",
            json={
                "name": name,
                "ip_address": ip_address,
                "port": port,
                "node_type": node_type
            }
        )
        if response.status_code == 201:
            node_id = response.json()["id"]
            logger.info(f"Node {name} registered with server. ID: {node_id}")
            return node_id
        else:
            logger.error(f"Failed to register node {name}: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Registration error for node {name}: {str(e)}")
        return None

def send_heartbeat(backend_url, node_id, node_name):
    """Envía heartbeat al servidor"""
    while True:
        if node_id in nodes and not nodes[node_id].get("simulate_failure", False):
            try:
                response = requests.post(
                    f"{backend_url}/monitoring/nodes/{node_id}/heartbeat/"
                )
                if response.status_code == 200:
                    nodes[node_id]["last_heartbeat_sent"] = time.time()
                    logger.info(f"Node {node_name} sent heartbeat at {time.ctime(nodes[node_id]['last_heartbeat_sent'])}")
                else:
                    logger.warning(f"Node {node_name} failed to send heartbeat: {response.text}")
            except Exception as e:
                logger.error(f"Node {node_name} heartbeat error: {str(e)}")
        elif node_id in nodes and nodes[node_id].get("simulate_failure", False):
            logger.info(f"Node {node_name} simulating failure - no heartbeat sent")
        
        # Esperar un tiempo aleatorio entre 25 y 35 segundos para simular variabilidad
        time.sleep(random.uniform(25, 35))

def start_node_server(node_id, port):
    """Inicia un servidor HTTP para el nodo"""
    server = ThreadedHTTPServer(("0.0.0.0", port), NodeHTTPHandler, node_id)
    logger.info(f"Node server started at port {port}")
    server.serve_forever()

def simulate_node(name, backend_url, port=0, node_type='other'):
    """Simula un nodo completo"""
    # Si el puerto es 0, asignar uno aleatorio entre 5000 y 5999
    if port == 0:
        port = random.randint(5000, 5999)
    
    # Usar localhost para simulación local
    ip_address = "127.0.0.1"
    
    # Registrar el nodo con el servidor
    node_id = register_with_server(backend_url, name, ip_address, port, node_type)
    
    if node_id:
        # Inicializar estado del nodo
        nodes[node_id] = {
            "name": name,
            "ip_address": ip_address,
            "port": port,
            "node_type": node_type,
            "last_heartbeat_sent": None,
            "simulate_failure": False
        }
        
        # Iniciar thread para enviar heartbeats
        heartbeat_thread = threading.Thread(
            target=send_heartbeat,
            args=(backend_url, node_id, name),
            daemon=True
        )
        heartbeat_thread.start()
        
        # Iniciar servidor HTTP para el nodo
        server_thread = threading.Thread(
            target=start_node_server,
            args=(node_id, port),
            daemon=True
        )
        server_thread.start()
        
        return node_id, port
    
    return None, port

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Simulate heartbeat nodes')
    parser.add_argument('--name', type=str, default='Node', help='Base name for the nodes')
    parser.add_argument('--count', type=int, default=1, help='Number of nodes to simulate')
    parser.add_argument('--port', type=int, default=0, help='Starting port (0 for random)')
    parser.add_argument('--type', type=str, default='other', help='Node type (api, db, web, worker, other)')
    parser.add_argument('--backend', type=str, default='http://localhost:8000/api', help='Backend URL')
    
    args = parser.parse_args()
    
    logger.info(f"Starting {args.count} node(s) with base name '{args.name}' and type '{args.type}'")
    
    # Crear los nodos
    created_nodes = []
    for i in range(args.count):
        node_name = f"{args.name}-{i+1}" if args.count > 1 else args.name
        port = args.port + i if args.port > 0 else 0
        
        node_id, actual_port = simulate_node(node_name, args.backend, port, args.type)
        if node_id:
            created_nodes.append((node_id, node_name, actual_port))
    
    if created_nodes:
        logger.info(f"Created {len(created_nodes)} nodes:")
        for node_id, name, port in created_nodes:
            logger.info(f"  - {name} (ID: {node_id}) on port {port}")
        
        # Mantener el script en ejecución
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down nodes...")
            sys.exit(0)
    else:
        logger.error("Failed to create any nodes")
        sys.exit(1)

if __name__ == "__main__":
    main()