# appointments/models.py
from django.db import models
from accounts.models import User
from barbers.models import BarberProfile
from services.models import Service
from schedules.models import TimeSlot

class Appointment(models.Model):
    """Citas de los clientes con los barberos"""
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (PENDING, 'Pendiente'),
        (CONFIRMED, 'Confirmada'),
        (COMPLETED, 'Completada'),
        (CANCELLED, 'Cancelada'),
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    barber = models.ForeignKey(BarberProfile, on_delete=models.CASCADE, related_name='appointments')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.customer.get_full_name()} con {self.barber.user.get_full_name()} - {self.date} {self.time_slot.start_time}"