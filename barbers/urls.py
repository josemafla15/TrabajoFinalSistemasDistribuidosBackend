# barbers/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BarberProfileViewSet, SpecialtyViewSet, BarberSpecialtyViewSet

router = DefaultRouter()
router.register(r'profiles', BarberProfileViewSet)
router.register(r'specialties', SpecialtyViewSet)
router.register(r'barber-specialties', BarberSpecialtyViewSet)

urlpatterns = [
    path('', include(router.urls)),
]