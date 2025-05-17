# monitoring/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Node, ServiceStatus
from .serializers import NodeSerializer, ServiceStatusSerializer
import uuid
import logging
import json



logger = logging.getLogger(__name__)

class NodeViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar nodos de monitoreo.
    """
    queryset = Node.objects.all()
    serializer_class = NodeSerializer
    
    @action(detail=True, methods=['post'])
    def heartbeat(self, request, pk=None):
        """
        Registra un latido (heartbeat) de un nodo.
        """
        try:
            node = self.get_object()
            node.last_heartbeat = timezone.now()
            node.save()
            return Response({'status': 'heartbeat recorded'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        Retorna solo los nodos activos.
        """
        active_nodes = Node.objects.filter(is_active=True)
        serializer = self.get_serializer(active_nodes, many=True)
        return Response(serializer.data)

class ServiceStatusViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar estados de servicios.
    """
    queryset = ServiceStatus.objects.all()
    serializer_class = ServiceStatusSerializer
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """
        Actualiza el estado operacional de un servicio.
        """
        try:
            service = self.get_object()
            is_operational = request.data.get('is_operational', None)
            
            if is_operational is not None:
                service.is_operational = is_operational
                service.save()
                return Response({'status': 'service status updated'})
            else:
                return Response({'error': 'is_operational field is required'}, 
                               status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Funciones de vista adicionales para las URLs definidas

@api_view(['POST'])
@csrf_exempt
@permission_classes([AllowAny])
def register_node(request):
    """
    Registra un nuevo nodo en el sistema de monitoreo.
    """
    serializer = NodeSerializer(data=request.data)
    if serializer.is_valid():
        node = serializer.save(last_heartbeat=timezone.now())
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def check_nodes(request):
    """
    Verifica el estado de todos los nodos y retorna un resumen.
    """
    nodes = Node.objects.all()
    active_nodes = [node for node in nodes if node.is_alive]
    
    return Response({
        'total_nodes': nodes.count(),
        'active_nodes': len(active_nodes),
        'inactive_nodes': nodes.count() - len(active_nodes)
    })

@api_view(['GET'])
def check_services(request):
    """
    Verifica el estado de todos los servicios y retorna un resumen.
    """
    services = ServiceStatus.objects.all()
    operational_services = services.filter(is_operational=True)
    
    return Response({
        'total_services': services.count(),
        'operational_services': operational_services.count(),
        'non_operational_services': services.count() - operational_services.count()
    })

@api_view(['POST'])
@csrf_exempt
def update_service_status(request, service_id):
    """
    Actualiza el estado de un servicio específico.
    """
    try:
        service = get_object_or_404(ServiceStatus, id=service_id)
        is_operational = request.data.get('is_operational', None)
        
        if is_operational is not None:
            service.is_operational = is_operational
            service.save()
            return Response({'status': 'service status updated'})
        else:
            return Response({'error': 'is_operational field is required'}, 
                           status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error updating service {service_id}: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

def dashboard(request):
    """
    Vista para el dashboard de monitoreo.
    """
    nodes = Node.objects.all()
    services = ServiceStatus.objects.all()
    
    # Calcular estadísticas
    total_nodes = nodes.count()
    active_nodes = sum(1 for node in nodes if node.is_alive)
    
    total_services = services.count()
    operational_services = services.filter(is_operational=True).count()
    
    context = {
        'nodes': nodes,
        'services': services,
        'stats': {
            'total_nodes': total_nodes,
            'active_nodes': active_nodes,
            'inactive_nodes': total_nodes - active_nodes,
            'total_services': total_services,
            'operational_services': operational_services,
            'non_operational_services': total_services - operational_services,
        }
    }
    
    return render(request, 'monitoring/dashboard.html', context)

@api_view(['POST'])
@csrf_exempt
@permission_classes([AllowAny])
def create_node(request):
    """
    Crea un nuevo nodo con los datos proporcionados.
    """
    serializer = NodeSerializer(data=request.data)
    if serializer.is_valid():
        node = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@csrf_exempt
@permission_classes([AllowAny])
def create_multiple_nodes(request):
    """
    Crea múltiples nodos a partir de una lista de datos.
    """
    if not isinstance(request.data, list):
        return Response({'error': 'Expected a list of nodes'}, status=status.HTTP_400_BAD_REQUEST)
    
    created_nodes = []
    errors = []
    
    for node_data in request.data:
        serializer = NodeSerializer(data=node_data)
        if serializer.is_valid():
            node = serializer.save()
            created_nodes.append(serializer.data)
        else:
            errors.append({
                'data': node_data,
                'errors': serializer.errors
            })
    
    if not errors:
        return Response(created_nodes, status=status.HTTP_201_CREATED)
    
    return Response({
        'created_nodes': created_nodes,
        'errors': errors
    }, status=status.HTTP_207_MULTI_STATUS if created_nodes else status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@csrf_exempt
@permission_classes([AllowAny])
def node_heartbeat(request, node_id=None):
    """
    Actualiza el heartbeat de un nodo y almacena métricas.
    Si no se proporciona node_id, intenta identificar el nodo por IP o crear uno nuevo.
    """
    try:
        # Obtener datos del request
        data = request.data
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                return Response({'error': 'Invalid JSON data'}, status=status.HTTP_400_BAD_REQUEST)
        
        metrics = data.get('metrics', {})
        ip_address = data.get('ip_address')
        name = data.get('name', f"Node-{ip_address}")
        
        node = None
        
        # Buscar nodo existente
        if node_id:
            try:
                node = Node.objects.get(id=node_id)
            except Node.DoesNotExist:
                pass
        
        if not node and ip_address:
            try:
                node = Node.objects.get(ip_address=ip_address)
            except Node.DoesNotExist:
                # Crear nodo si no existe
                if ip_address:
                    node = Node.objects.create(
                        name=name,
                        ip_address=ip_address,
                        last_heartbeat=timezone.now()
                    )
                    logger.info(f"Nuevo nodo creado: {name} ({ip_address})")
                else:
                    return Response({'error': 'Se requiere ip_address para crear un nuevo nodo'}, 
                                  status=status.HTTP_400_BAD_REQUEST)
        
        if not node:
            return Response({'error': 'No se pudo encontrar o crear el nodo'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Actualizar heartbeat
        node.last_heartbeat = timezone.now()
        
        # Actualizar métricas si se proporcionan
        if hasattr(node, 'cpu_usage') and 'cpu' in metrics:
            node.cpu_usage = metrics['cpu']
        if hasattr(node, 'memory_usage') and 'memory' in metrics:
            node.memory_usage = metrics['memory']
        if hasattr(node, 'disk_usage') and 'disk' in metrics:
            node.disk_usage = metrics['disk']
        if hasattr(node, 'system_info') and 'system_info' in metrics:
            node.system_info = metrics['system_info']
        
        node.save()
        logger.info(f"Heartbeat recibido de nodo {node.name} ({node.ip_address})")
        
        return Response({
            'status': 'heartbeat recorded',
            'node': {
                'id': node.id,
                'name': node.name,
                'status': getattr(node, 'status_display', 'active')
            }
        })
    except Exception as e:
        logger.error(f"Error al procesar heartbeat: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
def raw_node_heartbeat(request):
    """
    Endpoint para heartbeat sin usar DRF, completamente exento de CSRF.
    """
    # Depuración detallada
    logger.info("=" * 50)
    logger.info("INICIO DE DEPURACIÓN DE HEARTBEAT")
    logger.info(f"Método: {request.method}")
    logger.info(f"Path: {request.path}")
    logger.info(f"Headers: {dict(request.headers.items())}")
    logger.info(f"GET params: {request.GET}")
    logger.info(f"POST params: {request.POST}")
    try:
        body_content = request.body.decode('utf-8')
        logger.info(f"Body: {body_content[:200]}")
    except Exception as e:
        logger.info(f"No se pudo decodificar el body: {str(e)}")
    logger.info("FIN DE DEPURACIÓN DE HEARTBEAT")
    logger.info("=" * 50)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    
    try:
        # Parsear manualmente el JSON
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        
        ip_address = data.get('ip_address')
        name = data.get('name', f"Node-{ip_address}")
        metrics = data.get('metrics', {})
        
        if not ip_address:
            return JsonResponse({'error': 'ip_address is required'}, status=400)
        
        # Buscar o crear nodo
        try:
            node = Node.objects.get(ip_address=ip_address)
        except Node.DoesNotExist:
            # Crear nodo si no existe
            node = Node.objects.create(
                name=name,
                ip_address=ip_address,
                last_heartbeat=timezone.now()
            )
            logger.info(f"Nuevo nodo creado: {name} ({ip_address})")
        
        # Actualizar heartbeat
        node.last_heartbeat = timezone.now()
        
        # Actualizar métricas si se proporcionan y existen los campos
        if hasattr(node, 'cpu_usage') and 'cpu' in metrics:
            node.cpu_usage = metrics['cpu']
        if hasattr(node, 'memory_usage') and 'memory' in metrics:
            node.memory_usage = metrics['memory']
        if hasattr(node, 'disk_usage') and 'disk' in metrics:
            node.disk_usage = metrics['disk']
        if hasattr(node, 'system_info') and 'system_info' in metrics:
            node.system_info = metrics['system_info']
        
        node.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Heartbeat recorded',
            'node_id': str(node.id),
            'node_name': node.name
        })
        
    except Exception as e:
        logger.error(f"Error al procesar heartbeat: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)
    

@csrf_exempt
def simple_heartbeat(request):
    """
    Endpoint extremadamente simple para heartbeat, sin ninguna validación.
    Solo para pruebas.
    """
    logger.info("=" * 50)
    logger.info("SIMPLE HEARTBEAT RECIBIDO")
    logger.info(f"Método: {request.method}")
    logger.info(f"Headers: {dict(request.headers.items())}")
    try:
        body_content = request.body.decode('utf-8')
        logger.info(f"Body: {body_content[:200]}")
    except Exception as e:
        logger.info(f"No se pudo decodificar el body: {str(e)}")
    logger.info("=" * 50)
    
    return JsonResponse({
        'status': 'success',
        'message': 'Simple heartbeat recibido',
        'timestamp': timezone.now().isoformat()
    })