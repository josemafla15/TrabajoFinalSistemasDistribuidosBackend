# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """Modelo extendido de usuario para clientes y barberos"""
    CUSTOMER = 'customer'
    BARBER = 'barber'
    ADMIN = 'admin'
    
    ROLE_CHOICES = [
        (CUSTOMER, 'Cliente'),
        (BARBER, 'Barbero'),
        (ADMIN, 'Administrador'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=CUSTOMER)
    phone_number = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    
    def is_barber(self):
        return self.role == self.BARBER
    
    def is_customer(self):
        return self.role == self.CUSTOMER