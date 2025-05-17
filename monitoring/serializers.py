# monitoring/serializers.py
from rest_framework import serializers
from .models import Node, ServiceStatus

class NodeSerializer(serializers.ModelSerializer):
    is_alive = serializers.BooleanField(read_only=True)
    status_display = serializers.CharField(read_only=True)
    
    class Meta:
        model = Node
        fields = ['id', 'name', 'ip_address', 'port', 'node_type', 'last_heartbeat', 
                  'is_active', 'is_alive', 'status_display', 'created_at', 'updated_at']
        read_only_fields = ['id', 'last_heartbeat', 'created_at', 'updated_at']

class ServiceStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceStatus
        fields = ['id', 'name', 'description', 'is_operational', 'last_check', 'nodes']
        read_only_fields = ['id', 'last_check']