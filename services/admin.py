from django.contrib import admin
from .models import Service

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration_minutes', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active',)
    # Elimina esta línea si no deseas usar un 'slug'
    # prepopulated_fields = {'slug': ('name',)} 
    
admin.site.register(Service, ServiceAdmin)
