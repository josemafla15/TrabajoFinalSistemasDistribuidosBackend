# appointments/views.py
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Appointment
from .serializers import AppointmentSerializer

class IsCustomerOrBarberOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (obj.customer == request.user or 
                obj.barber.user == request.user or 
                request.user.is_staff)

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['date', 'time_slot__start_time', 'created_at']
    ordering = ['date', 'time_slot__start_time']
    
    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsCustomerOrBarberOrAdmin()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        
        # Filtrado base según el tipo de usuario
        if user.is_staff:
            queryset = Appointment.objects.all()
        elif hasattr(user, 'is_barber') and user.is_barber():
            queryset = Appointment.objects.filter(barber__user=user)
        else:
            # Cliente normal
            queryset = Appointment.objects.filter(customer=user)
        
        # Filtros adicionales
        customer = self.request.query_params.get('customer')
        if customer and user.is_staff:  # Solo admin puede filtrar por cliente
            queryset = queryset.filter(customer=customer)
        
        barber = self.request.query_params.get('barber')
        if barber:
            queryset = queryset.filter(barber=barber)
        
        service = self.request.query_params.get('service')
        if service:
            queryset = queryset.filter(service=service)
        
        date = self.request.query_params.get('date')
        if date:
            queryset = queryset.filter(date=date)
        
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        return queryset
    
    # Añadimos este método para manejar la creación de citas
    def create(self, request, *args, **kwargs):
        """
        Sobrescribe el método create para asignar automáticamente el usuario autenticado
        como el cliente (customer) de la cita.
        """
        # Copiamos los datos para no modificar el request original
        data = request.data.copy()
        
        # Asignamos el usuario autenticado como cliente
        # No es necesario incluir esto en los datos ya que el serializer lo hará,
        # pero lo dejamos por claridad
        data['customer'] = request.user.id
        
        # Creamos el serializer con los datos y el contexto
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def perform_create(self, serializer):
        """
        Método que realiza la creación del objeto.
        Asegura que el cliente sea el usuario autenticado.
        """
        serializer.save(customer=self.request.user)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        appointment = self.get_object()
        
        # Verificar si el usuario tiene permiso para cancelar
        if not (appointment.customer == request.user or 
                appointment.barber.user == request.user or 
                request.user.is_staff):
            return Response(
                {"detail": "No tienes permiso para cancelar esta cita."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Verificar si la cita ya está cancelada o completada
        if appointment.status in [Appointment.CANCELLED, Appointment.COMPLETED]:
            return Response(
                {"detail": f"No se puede cancelar una cita con estado {appointment.get_status_display()}."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        appointment.status = Appointment.CANCELLED
        appointment.save()
        
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        appointment = self.get_object()
        
        # Solo el barbero o admin puede marcar como completada
        if not (appointment.barber.user == request.user or request.user.is_staff):
            return Response(
                {"detail": "Solo el barbero o un administrador puede marcar una cita como completada."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Verificar si la cita ya está cancelada o completada
        if appointment.status in [Appointment.CANCELLED, Appointment.COMPLETED]:
            return Response(
                {"detail": f"No se puede completar una cita con estado {appointment.get_status_display()}."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        appointment.status = Appointment.COMPLETED
        appointment.save()
        
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)