# monitoring/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'nodes', views.NodeViewSet)
router.register(r'services', views.ServiceStatusViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('nodes/register/', views.register_node, name='register-node'),
    path('nodes/<uuid:node_id>/heartbeat/', views.node_heartbeat, name='node-heartbeat'),
    path('nodes/check/', views.check_nodes, name='check-nodes'),
    path('services/check/', views.check_services, name='check-services'),
    path('services/<uuid:service_id>/update/', views.update_service_status, name='update-service-status'),
    path('dashboard/', views.dashboard, name='monitoring-dashboard'),
    path('nodes/create/', views.create_node, name='create-node'),
    path('nodes/create-multiple/', views.create_multiple_nodes, name='create-multiple-nodes'),
    path('nodes/heartbeat/', views.node_heartbeat, name='node-heartbeat-by-ip'),
    path('raw/heartbeat/', views.raw_node_heartbeat, name='raw-node-heartbeat'),
    path('simple/heartbeat/', views.simple_heartbeat, name='simple-heartbeat'),

    # Añade estas líneas si no existen
    path('raw/heartbeat/', views.raw_node_heartbeat, name='raw-node-heartbeat'),
    path('simple/heartbeat/', views.simple_heartbeat, name='simple-heartbeat'),
    
]