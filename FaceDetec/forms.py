from django import forms
from .models import Attendance

class UserForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['name', 'age']
