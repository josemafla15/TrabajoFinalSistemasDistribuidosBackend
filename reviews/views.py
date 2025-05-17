# reviews/views.py
from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from .models import Review
from .serializers import ReviewSerializer
from appointments.models import Appointment

class IsCustomerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.customer == request.user

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsCustomerOrReadOnly()]
        return [permissions.AllowAny()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por cliente
        customer = self.request.query_params.get('customer')
        if customer:
            queryset = queryset.filter(customer=customer)
        
        # Filtrar por barbero
        barber = self.request.query_params.get('barber')
        if barber:
            queryset = queryset.filter(barber=barber)
        
        # Filtrar por calificación
        rating = self.request.query_params.get('rating')
        if rating:
            queryset = queryset.filter(rating=rating)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        # Verificar si el usuario es un cliente
        if not request.user.is_customer():
            return Response(
                {"detail": "Solo los clientes pueden dejar reseñas."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Si se proporciona un appointment_id, verificar que la cita esté completada
        appointment_id = request.data.get('appointment')
        if appointment_id:
            try:
                appointment = Appointment.objects.get(id=appointment_id)
                
                # Verificar que el cliente sea el dueño de la cita
                if appointment.customer != request.user:
                    return Response(
                        {"detail": "Solo puedes dejar reseñas de tus propias citas."},
                        status=status.HTTP_403_FORBIDDEN
                    )
                
                # Verificar que la cita esté completada
                if appointment.status != Appointment.COMPLETED:
                    return Response(
                        {"detail": "Solo puedes dejar reseñas de citas completadas."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Verificar si ya existe una reseña para esta cita
                if Review.objects.filter(appointment=appointment).exists():
                    return Response(
                        {"detail": "Ya has dejado una reseña para esta cita."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            except Appointment.DoesNotExist:
                return Response(
                    {"detail": "La cita especificada no existe."},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Asignar automáticamente el cliente actual
        request.data['customer'] = request.user.id
        
        return super().create(request, *args, **kwargs)