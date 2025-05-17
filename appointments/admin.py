from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        'id',  # Mostrar el ID de la cita
        'get_customer_name',
        'get_customer_id',  # ID del cliente
        'get_barber_name',
        'get_barber_id',  # ID del barbero
        'service',
        'date',
        'get_time_slot',
        'status',
        'created_at'
    )
    list_filter = ('status', 'date', 'barber', 'service')
    search_fields = ('customer__first_name', 'customer__last_name', 'barber__user__first_name', 'barber__user__last_name')
    ordering = ('-date', '-created_at')
    readonly_fields = ('created_at', 'updated_at')

    def get_customer_name(self, obj):
        return obj.customer.get_full_name()
    get_customer_name.short_description = 'Cliente'

    def get_customer_id(self, obj):
        return obj.customer.id  # Devuelve el ID del cliente
    get_customer_id.short_description = 'ID Cliente'

    def get_barber_name(self, obj):
        return obj.barber.user.get_full_name()
    get_barber_name.short_description = 'Barbero'

    def get_barber_id(self, obj):
        return obj.barber.id  # Devuelve el ID del barbero
    get_barber_id.short_description = 'ID Barbero'

    def get_time_slot(self, obj):
        return f"{obj.time_slot.start_time} - {obj.time_slot.end_time}"
    get_time_slot.short_description = 'Horario'
