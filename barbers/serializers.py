# barbers/serializers.py
from rest_framework import serializers
from .models import BarberProfile, Specialty, BarberSpecialty
from accounts.serializers import UserSerializer

class SpecialtySerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialty
        fields = ['id', 'name', 'description']

class BarberSpecialtySerializer(serializers.ModelSerializer):
    specialty = SpecialtySerializer(read_only=True)
    specialty_id = serializers.PrimaryKeyRelatedField(
        queryset=Specialty.objects.all(),
        source='specialty',
        write_only=True
    )
    
    class Meta:
        model = BarberSpecialty
        fields = ['id', 'specialty', 'specialty_id']

class BarberProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    specialties = BarberSpecialtySerializer(many=True, read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    
    class Meta:
        model = BarberProfile
        fields = ['id', 'user', 'bio', 'years_of_experience', 'instagram_profile', 'specialties', 'average_rating']