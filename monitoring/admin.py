# monitoring/admin.py
from django.contrib import admin
from .models import Node, ServiceStatus

@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'node_type', 'ip_address', 'port', 'last_heartbeat', 'is_active', 'is_alive_display')
    list_filter = ('is_active', 'node_type')
    search_fields = ('name', 'ip_address')
    readonly_fields = ('id', 'created_at', 'updated_at', 'last_heartbeat')
    
    def is_alive_display(self, obj):
        return obj.is_alive
    is_alive_display.boolean = True
    is_alive_display.short_description = "¿Activo?"

@admin.register(ServiceStatus)
class ServiceStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_operational', 'last_check')
    list_filter = ('is_operational',)
    search_fields = ('name', 'description')
    readonly_fields = ('id', 'last_check')
    filter_horizontal = ('nodes',)