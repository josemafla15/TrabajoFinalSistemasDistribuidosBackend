# monitoring/models.py
from django.db import models
import uuid
from django.utils import timezone
from django.conf import settings

class Node(models.Model):
    """Modelo para representar un nodo en el sistema"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    port = models.IntegerField(default=5000)
    node_type = models.CharField(max_length=50, choices=[
        ('api', 'API Server'),
        ('db', 'Database Server'),
        ('web', 'Web Server'),
        ('worker', 'Worker Node'),
        ('other', 'Other')
    ], default='other')
    last_heartbeat = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.ip_address}:{self.port})"
    
    @property
    def is_alive(self):
        """Verifica si el nodo está vivo basado en su último heartbeat"""
        if not self.last_heartbeat:
            return False
        
        # Considera un nodo como caído si no ha enviado heartbeat en el tiempo configurado
        threshold = timezone.now() - timezone.timedelta(
            seconds=getattr(settings, 'HEARTBEAT_FAILURE_THRESHOLD', 120)
        )
        return self.last_heartbeat >= threshold
    
    @property
    def status_display(self):
        """Devuelve el estado del nodo como texto"""
        if not self.is_active:
            return "Inactivo"
        return "Activo" if self.is_alive else "Caído"
    
    @property
    def endpoint(self):
        """Devuelve el endpoint completo del nodo"""
        return f"http://{self.ip_address}:{self.port}"

class ServiceStatus(models.Model):
    """Modelo para representar el estado de un servicio de la barbería"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_operational = models.BooleanField(default=True)
    last_check = models.DateTimeField(auto_now=True)
    
    # Relación con nodos (opcional)
    nodes = models.ManyToManyField(Node, blank=True, related_name='services')
    
    def __str__(self):
        return f"{self.name} - {'Operativo' if self.is_operational else 'No operativo'}"