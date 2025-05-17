# schedules/admin.py
from django.contrib import admin
from .models import WorkDay, TimeSlot
from .forms import WorkDayAdminForm

@admin.register(WorkDay)
class WorkDayAdmin(admin.ModelAdmin):
    form = WorkDayAdminForm
    list_display = ['barber', 'day_of_week', 'start_time', 'end_time', 'is_working']

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['work_day', 'start_time', 'end_time', 'is_available']
