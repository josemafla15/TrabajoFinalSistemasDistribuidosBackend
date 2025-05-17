# schedules/forms.py
from django import forms
from .models import WorkDay
from barbers.models import BarberProfile

class WorkDayAdminForm(forms.ModelForm):
    class Meta:
        model = WorkDay
        fields = '__all__'

    barber = forms.ModelChoiceField(
        queryset=BarberProfile.objects.all(),
        label='Barbero',
        widget=forms.Select(),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['barber'].label_from_instance = lambda obj: str(obj.user) if obj.user else f'Barber #{obj.id}'

