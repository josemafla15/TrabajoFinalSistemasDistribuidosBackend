#Urls de la aplicación principal del proyecto
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken.views import obtain_auth_token  # Asegúrate de importar este

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/barbers/', include('barbers.urls')),
    path('api/services/', include('services.urls')),
    path('api/schedules/', include('schedules.urls')),
    path('api/appointments/', include('appointments.urls')),
    path('api/reviews/', include('reviews.urls')),
    path('api/auth/token/', obtain_auth_token, name='obtain_token'),  # Aquí está la URL para obtener el token
    path('api-auth/', include('rest_framework.urls')),
    # Nueva URL para monitoreo
    path('api/monitoring/', include('monitoring.urls')),
    path('admin/', admin.site.urls),
    # Asegúrate de que esta línea exista y esté correcta
    path('monitoring/', include('monitoring.urls')),
    # Otras rutas...
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
