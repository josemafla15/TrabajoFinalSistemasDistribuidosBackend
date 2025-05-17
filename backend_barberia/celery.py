# backend_barberia/celery.py
import os
from celery import Celery

# Establecer la variable de entorno para configuraciones de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_barberia.settings')

# Crear la instancia de la aplicación Celery
app = Celery('backend_barberia')

# Cargar configuración desde settings.py usando namespace 'CELERY'
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodescubrir tareas en todas las aplicaciones registradas
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')