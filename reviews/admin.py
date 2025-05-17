# reviews/admin.py

from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'get_customer_name',
        'get_customer_id',
        'get_barber_name',
        'get_barber_id',
        'appointment',
        'rating',
        'created_at'
    )
    list_filter = ('rating', 'created_at')
    search_fields = (
        'customer__first_name', 'customer__last_name',
        'barber__user__first_name', 'barber__user__last_name'
    )
    ordering = ('-created_at',)

    def get_customer_name(self, obj):
        return obj.customer.get_full_name()
    get_customer_name.short_description = 'Cliente'

    def get_customer_id(self, obj):
        return obj.customer.id
    get_customer_id.short_description = 'ID Cliente'

    def get_barber_name(self, obj):
        return obj.barber.user.get_full_name()
    get_barber_name.short_description = 'Barbero'

    def get_barber_id(self, obj):
        return obj.barber.user.id
    get_barber_id.short_description = 'ID Barbero'
