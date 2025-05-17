# monitoring/tasks.py
from celery import shared_task
from django.utils import timezone
from django.conf import settings
import logging
from .models import Node, ServiceStatus
import requests

logger = logging.getLogger(__name__)

@shared_task
def check_nodes_heartbeat():
    """Verifica el estado de todos los nodos registrados"""
    nodes = Node.objects.filter(is_active=True)
    dead_nodes = []
    
    # Umbral de tiempo para considerar un nodo como caído
    threshold = timezone.now() - timezone.timedelta(
        seconds=getattr(settings, 'HEARTBEAT_FAILURE_THRESHOLD', 120)
    )
    
    for node in nodes:
        if not node.last_heartbeat or node.last_heartbeat < threshold:
            dead_nodes.append(node)
            logger.warning(f"Node {node.name} ({node.ip_address}:{node.port}) is down!")
            
            # Actualizar servicios relacionados si es necesario
            for service in node.services.all():
                # Si todos los nodos de un servicio están caídos, marcar el servicio como no operativo
                if all(not n.is_alive for n in service.nodes.all()):
                    service.is_operational = False
                    service.save()
                    logger.warning(f"Service {service.name} marked as non-operational due to all nodes being down")
    
    if dead_nodes:
        logger.warning(f"Found {len(dead_nodes)} dead nodes out of {nodes.count()} total nodes")
    else:
        logger.info(f"All {nodes.count()} nodes are alive")
    
    return f"Checked {nodes.count()} nodes, found {len(dead_nodes)} dead nodes"

@shared_task
def check_barbershop_services():
    """Verifica el estado de los servicios principales de la barbería"""
    # Lista de endpoints a verificar
    endpoints = [
        {'name': 'API de Citas', 'url': 'http://localhost:8000/api/appointments/'},
        {'name': 'API de Barberos', 'url': 'http://localhost:8000/api/barbers/'},
        {'name': 'API de Servicios', 'url': 'http://localhost:8000/api/services/'},
    ]
    
    for endpoint in endpoints:
        service_name = endpoint['name']
        service_url = endpoint['url']
        
        # Buscar o crear el servicio en la base de datos
        service, created = ServiceStatus.objects.get_or_create(
            name=service_name,
            defaults={'description': f"Endpoint: {service_url}"}
        )
        
        # Verificar si el servicio está operativo
        try:
            response = requests.get(service_url, timeout=5)
            is_operational = response.status_code < 400
        except Exception:
            is_operational = False
        
        # Actualizar el estado del servicio
        if service.is_operational != is_operational:
            service.is_operational = is_operational
            service.save()
            logger.info(f"Service {service_name} status changed to {'operational' if is_operational else 'non-operational'}")
    
    return "Checked barbershop services"