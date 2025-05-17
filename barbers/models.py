# barbers/models.py
from django.db import models
from accounts.models import User

class BarberProfile(models.Model):
    """Perfil extendido para barberos"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='barber_profile')
    bio = models.TextField(blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    instagram_profile = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - Barbero"
    
    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / reviews.count()
        return 0

class Specialty(models.Model):
    """Especialidades de los barberos"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class BarberSpecialty(models.Model):
    """Relación entre barberos y especialidades"""
    barber = models.ForeignKey(BarberProfile, on_delete=models.CASCADE, related_name='specialties')
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('barber', 'specialty')
        verbose_name_plural = 'Barber Specialties'
    
    def __str__(self):
        return f"{self.barber.user.get_full_name()} - {self.specialty.name}"