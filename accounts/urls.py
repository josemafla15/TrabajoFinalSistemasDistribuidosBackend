from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet
from rest_framework.authtoken.views import obtain_auth_token  # Asegúrate de importar esta vista
from django.views.decorators.csrf import csrf_exempt  # Importa csrf_exempt

# Crea el router
router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    # Rutas relacionadas con el viewset de UserViewSet
    path('', include(router.urls)),

    # Ruta para obtener el token de autenticación, no necesitas que esté dentro del router
    path('auth/token/', csrf_exempt(obtain_auth_token)),  # Deshabilitar CSRF para este endpoint
]
