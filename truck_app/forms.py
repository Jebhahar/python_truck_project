from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser



class CustomUserCreationForm(UserCreationForm):
    class Meta:
        print("CustomUserCreationForm")
        model = CustomUser
        fields = ['phone_number', 'password1', 'password2']

