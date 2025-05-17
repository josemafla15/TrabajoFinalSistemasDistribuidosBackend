# schedules/serializers.py
from rest_framework import serializers
from .models import WorkDay, TimeSlot

class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ['id', 'start_time', 'end_time', 'is_available']

class WorkDaySerializer(serializers.ModelSerializer):
    time_slots = TimeSlotSerializer(many=True, read_only=True)
    day_name = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkDay
        fields = ['id', 'barber', 'day_of_week', 'day_name', 'start_time', 'end_time', 'is_working', 'time_slots']
    
    def get_day_name(self, obj):
        return obj.get_day_of_week_display()