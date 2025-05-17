# schedules/models.py
from django.db import models
from barbers.models import BarberProfile

class WorkDay(models.Model):
    """Días de trabajo de los barberos"""
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6
    
    DAY_CHOICES = [
        (MONDAY, 'Lunes'),
        (TUESDAY, 'Martes'),
        (WEDNESDAY, 'Miércoles'),
        (THURSDAY, 'Jueves'),
        (FRIDAY, 'Viernes'),
        (SATURDAY, 'Sábado'),
        (SUNDAY, 'Domingo'),
    ]
    
    barber = models.ForeignKey(BarberProfile, on_delete=models.CASCADE, related_name='work_days')
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_working = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('barber', 'day_of_week')
    
    def __str__(self):
        return f"{self.barber.user.get_full_name()} - {self.get_day_of_week_display()}"

class TimeSlot(models.Model):
    """Slots de tiempo disponibles para citas"""
    work_day = models.ForeignKey(WorkDay, on_delete=models.CASCADE, related_name='time_slots')
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.work_day.barber.user.get_full_name()} - {self.work_day.get_day_of_week_display()} - {self.start_time} a {self.end_time}"