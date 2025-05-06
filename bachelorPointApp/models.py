from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.utils import timezone
# Create your models here.

 # Abstract user model for custom user creation
class CustomUser(AbstractUser):
    USER_TYPES = (
        ('bachelor', 'Bachelor'),
        ('house_owner', 'House Owner'),
        ('food_supplier', 'Food Supplier'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPES)

class EmailOTP(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

class Register(models.Model):
    name=models.CharField(max_length=30)
    email=models.EmailField(max_length=20)
    password=models.CharField(max_length=40)
    reset_password=models.CharField(max_length=40)
    def __str__(self):
        return self.email


class LogIn(models.Model):
   
    logInemail=models.ForeignKey(Register, on_delete=models.CASCADE, related_name='login_by_email')
    logInpassword=models.ForeignKey(Register, on_delete=models.CASCADE, related_name='login_by_password')
   
    def __str__(self):
        return self.email



class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=20, blank=True)
    gender = models.CharField(max_length=10, blank=True)
    dob = models.DateField(null=True, blank=True)
    profession = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)
    blood_group = models.CharField(max_length=5, blank=True)
    image = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.user.username}'s Profile"

class HouseOwner(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    House_name = models.CharField(max_length=30)
    PropertyId=models.IntegerField()
    Location=models.TextField(blank=True,null=True)
    category_choices=(
        ('House','house'),
        ('Sublet','sublet'),
        ('Hostel','hostel')
        )
    category=models.CharField(max_length=30,choices=category_choices)
    BedRoom=models.IntegerField()
    BathRoom=models.IntegerField()
    Belcony=models.IntegerField()
    Price=models.IntegerField()
    Availability=models.DateField()
    Description=models.TextField(blank=True,null=True)
    image1 = models.ImageField(upload_to='properties/')
    image2 = models.ImageField(upload_to='properties/')
    image3 = models.ImageField(upload_to='properties/')
    def __str__(self):
        return self.House_name
    
class FoodSupplier(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # Removed duplicate FoodId definition, keeping only one
    FoodId = models.IntegerField(null=True, blank=True, unique=True)  # Made optional
    Food_name = models.CharField(max_length=30)
    Location = models.TextField(blank=True, null=True)
    category_choices = (
        ('Veg', 'veg'),
        ('Non-Veg', 'non-veg')
    )
    category = models.CharField(max_length=30, choices=category_choices)
    Price = models.IntegerField(null=True, blank=True, unique=True)
    Description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.Food_name
    
class AvailableHouse(models.Model):
    owner = models.ForeignKey(HouseOwner, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='house/')
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.title
    
class AvailableFoods(models.Model):
    supplier = models.ForeignKey(FoodSupplier, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    details = models.TextField()
    image = models.ImageField(upload_to='foods/')
    duration = models.CharField(max_length=100, blank=True)  # e.g., "30 days (can be customized)"
    meals_per_day = models.CharField(max_length=100, blank=True)  # e.g., "2 (Breakfast+Lunch)"
    price = models.CharField(max_length=100, blank=True)  # e.g., "BDT 6500 per month"
    def __str__(self):
        return self.name



class Order(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    food = models.ForeignKey(AvailableFoods, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=10, unique=True)
    items = models.TextField()
    time = models.TimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Accepted', 'Accepted'),
            ('Declined', 'Declined')
        ],
        default='Pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Order #{self.order_id}"

class Bill(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Paid', 'Paid'),
            ('Overdue', 'Overdue')
        ],
        default='Pending'
    )
    def __str__(self):
        return f"Bill for Order #{self.order.order_id}"

class Complaint(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=[
            ('Open', 'Open'),
            ('Resolved', 'Resolved'),
            ('Closed', 'Closed')
        ],
        default='Open'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Complaint #{self.id}"
    

from django.db import models
from django.contrib.auth.models import User

class AvailableHouse(models.Model):
    House_name = models.CharField(max_length=200)
    Property_id = models.CharField(max_length=20, unique=True)
    Location = models.CharField(max_length=200)
    Category = models.CharField(max_length=100)
    Price = models.DecimalField(max_digits=10, decimal_places=2)
    Availability = models.CharField(max_length=100)
    image1 = models.ImageField(upload_to='house_images/')
    image2 = models.ImageField(upload_to='house_images/', null=True, blank=True)
    image3 = models.ImageField(upload_to='house_images/', null=True, blank=True)

    def __str__(self):
        return self.House_name

class Tenant(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # Add other tenant-specific fields if needed

class BookingRequest(models.Model):
    house = models.ForeignKey(AvailableHouse, on_delete=models.CASCADE)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    date_requested = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Pending')

    def __str__(self):
        return f"{self.tenant.user.username} - {self.house.House_name}"