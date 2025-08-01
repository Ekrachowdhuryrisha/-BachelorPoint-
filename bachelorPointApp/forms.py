from django import forms                                                       # Import Django forms module
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm     # Import Django authentication forms
from .models import CustomUser, AvailableFoods, HouseOwner, AvailableHouse     # Import custom models

# Form for registering a new user, extending UserCreationForm
class CustomUserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)                                   # Email field, marked as required

    class Meta:
        model = CustomUser                                                    # Associate form with CustomUser model
        fields = ['username', 'email', 'user_type', 'password1', 'password2'] # Fields to include in the form

# Form for user login, extending AuthenticationForm
class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username or Email")                     # Username or email input field
    password = forms.CharField(label="Password", widget=forms.PasswordInput)  # Password input field with password widget

# Form for creating or updating available food listings
class AvailableFoodsForm(forms.ModelForm):
    class Meta:
        model = AvailableFoods                                               # Associate form with AvailableFoods model
        fields = ['name', 'location', 'details', 'image', 'duration', 'meals_per_day', 'price']  # Fields to include in the form

# Form for creating or updating house owner listings
class HouseOwnerForm(forms.ModelForm):
    class Meta:
        model = HouseOwner                                                   # Associate form with HouseOwner model
        fields = ['House_name', 'PropertyId', 'Location', 'category', 'BedRoom', 'BathRoom', 'Belcony', 'Price', 'Availability', 'Description', 'image1', 'image2', 'image3']  # Fields to include in the form
        widgets = {
            'Availability': forms.DateInput(attrs={'type': 'date'}),         # Date input widget for Availability field
            'Description': forms.Textarea(attrs={'rows': 4}),                # Textarea widget for Description field with 4 rows
            'Location': forms.Textarea(attrs={'rows': 2}),                   # Textarea widget for Location field with 2 rows
        }