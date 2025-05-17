# reviews/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User
from barbers.models import BarberProfile
from appointments.models import Appointment

class Review(models.Model):
    """Calificaciones y reseñas de los clientes a los barberos"""
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    barber = models.ForeignKey(BarberProfile, on_delete=models.CASCADE, related_name='reviews')
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='review', null=True, blank=True)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.customer.get_full_name()} calificó a {self.barber.user.get_full_name()} con {self.rating} estrellas"