# schedules/views.py
from rest_framework import viewsets, permissions, filters
from .models import WorkDay, TimeSlot
from .serializers import WorkDaySerializer, TimeSlotSerializer

class IsBarberOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.barber.user == request.user or request.user.is_staff

class WorkDayViewSet(viewsets.ModelViewSet):
    queryset = WorkDay.objects.all()
    serializer_class = WorkDaySerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsBarberOrAdmin()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por barbero
        barber = self.request.query_params.get('barber')
        if barber:
            queryset = queryset.filter(barber=barber)
        
        # Filtrar por día de la semana
        day_of_week = self.request.query_params.get('day_of_week')
        if day_of_week:
            queryset = queryset.filter(day_of_week=day_of_week)
        
        # Filtrar por si está trabajando
        is_working = self.request.query_params.get('is_working')
        if is_working is not None:
            is_working_bool = is_working.lower() == 'true'
            queryset = queryset.filter(is_working=is_working_bool)
        
        return queryset

class TimeSlotViewSet(viewsets.ModelViewSet):
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsBarberOrAdmin()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por día de trabajo
        work_day = self.request.query_params.get('work_day')
        if work_day:
            queryset = queryset.filter(work_day=work_day)
        
        # Filtrar por disponibilidad
        is_available = self.request.query_params.get('is_available')
        if is_available is not None:
            is_available_bool = is_available.lower() == 'true'
            queryset = queryset.filter(is_available=is_available_bool)
        
        return queryset