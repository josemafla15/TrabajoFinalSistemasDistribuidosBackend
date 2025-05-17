# barbers/admin.py
from django.contrib import admin
from .models import BarberProfile, Specialty, BarberSpecialty

# Primero definimos el Inline
class BarberSpecialtyInline(admin.TabularInline):
    model = BarberSpecialty
    extra = 1  # Esto permite agregar una especialidad al barbero

# Luego, definimos el Admin para el modelo BarberProfile
class BarberProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'years_of_experience', 'instagram_profile')
    search_fields = ['user__first_name', 'user__last_name', 'bio']
    list_filter = ('years_of_experience',)
    
    # Ahora podemos usar el Inline porque ya está definido
    inlines = [BarberSpecialtyInline]  # Usamos un inline para manejar las especialidades de los barberos

class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ['name', 'description']

# Registra los modelos en el admin
admin.site.register(BarberProfile, BarberProfileAdmin)
admin.site.register(Specialty, SpecialtyAdmin)
admin.site.register(BarberSpecialty)
