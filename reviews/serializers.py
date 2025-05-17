# reviews/serializers.py
from rest_framework import serializers
from .models import Review
from accounts.serializers import UserSerializer
from barbers.serializers import BarberProfileSerializer

class ReviewSerializer(serializers.ModelSerializer):
    customer_details = UserSerializer(source='customer', read_only=True)
    barber_details = BarberProfileSerializer(source='barber', read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'customer', 'customer_details', 'barber', 'barber_details',
            'appointment', 'rating', 'comment', 'created_at'
        ]
        read_only_fields = ['created_at']