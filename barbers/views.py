# barbers/views.py
from rest_framework import viewsets, permissions, filters
from .models import BarberProfile, Specialty, BarberSpecialty
from .serializers import BarberProfileSerializer, SpecialtySerializer, BarberSpecialtySerializer

class SpecialtyViewSet(viewsets.ModelViewSet):
    queryset = Specialty.objects.all()
    serializer_class = SpecialtySerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return super().get_permissions()

class BarberProfileViewSet(viewsets.ModelViewSet):
    queryset = BarberProfile.objects.all()
    serializer_class = BarberProfileSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__first_name', 'user__last_name', 'bio']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por especialidad
        specialty = self.request.query_params.get('specialties__specialty')
        if specialty:
            queryset = queryset.filter(specialties__specialty=specialty)
        
        return queryset

class BarberSpecialtyViewSet(viewsets.ModelViewSet):
    queryset = BarberSpecialty.objects.all()
    serializer_class = BarberSpecialtySerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por barbero
        barber = self.request.query_params.get('barber')
        if barber:
            queryset = queryset.filter(barber=barber)
        
        # Filtrar por especialidad
        specialty = self.request.query_params.get('specialty')
        if specialty:
            queryset = queryset.filter(specialty=specialty)
        
        return queryset