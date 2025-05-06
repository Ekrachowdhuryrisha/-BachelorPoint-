from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, AvailableFoods, HouseOwner, AvailableHouse

class CustomUserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'user_type', 'password1', 'password2']

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username or Email")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

class AvailableFoodsForm(forms.ModelForm):
    class Meta:
        model = AvailableFoods
        fields = ['name', 'location', 'details', 'image', 'duration', 'meals_per_day', 'price']


class HouseOwnerForm(forms.ModelForm):
    class Meta:
        model = HouseOwner
        fields = ['House_name', 'PropertyId', 'Location', 'category', 'BedRoom', 'BathRoom', 'Belcony', 'Price', 'Availability', 'Description', 'image1', 'image2', 'image3']
        widgets = {
            'Availability': forms.DateInput(attrs={'type': 'date'}),
            'Description': forms.Textarea(attrs={'rows': 4}),
            'Location': forms.Textarea(attrs={'rows': 2}),
        }

class HouseForm(forms.ModelForm):
    class Meta:
        model = AvailableHouse
        fields = ['House_name', 'Property_id', 'Location', 'Category', 'Price', 'Availability', 'image1', 'image2', 'image3']