from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.utils import timezone

# Django models for a housing and food service platform
# Defines database structure for user management, profiles, houses, food items, orders, bills, and complaints.

# Custom user model extending Django's AbstractUser
class CustomUser(AbstractUser):
    """
    Custom user model to support different user types (Bachelor, House Owner, Food Supplier).
    - Extends AbstractUser to inherit default user fields (username, email, password, etc.).
    - Adds user_type field to categorize users.
    """
    USER_TYPES = (
        ('bachelor', 'Bachelor'),
        ('house_owner', 'House Owner'),
        ('food_supplier', 'Food Supplier'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPES)

# Model for storing email OTPs for user verification
class EmailOTP(models.Model):
    """
    Stores one-time passwords (OTPs) for email verification.
    - Linked to a CustomUser via OneToOneField.
    - Stores a 6-digit OTP and creation timestamp.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

# Model for user registration
class Register(models.Model):
    """
    Stores user registration details (possibly unused or legacy).
    - Contains name, email, password, and reset_password fields.
    - Note: Likely redundant due to CustomUser model; consider removing.
    """
    name = models.CharField(max_length=30)
    email = models.EmailField(max_length=20)
    password = models.CharField(max_length=40)
    reset_password = models.CharField(max_length=40)
    def __str__(self):
        return self.email

# Model for login 
class LogIn(models.Model):
    """
    Model for login credentials (possibly unused or flawed).
    - Links to Register model via ForeignKey for email and password.
    - Note: Incorrect design; authentication should use CustomUser. Consider removing.
    """
    logInemail = models.ForeignKey(Register, on_delete=models.CASCADE, related_name='login_by_email')
    logInpassword = models.ForeignKey(Register, on_delete=models.CASCADE, related_name='login_by_password')
    def __str__(self):
        return self.email

# User profile model
class Profile(models.Model):
    """
    Stores additional user information linked to CustomUser.
    - One-to-one relationship with the authenticated user.
    - Includes fields for name, mobile, gender, DOB, profession, address, blood group, and profile image.
    - Tracks last update timestamp.
    """
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

# Model for house owners and their properties
class HouseOwner(models.Model):
    """
    Stores house details listed by house owners.
    - Linked to a CustomUser via ForeignKey.
    - Includes house name, property ID, location, category, bedroom/bathroom/balcony count, price, availability, description, and up to three images.
    - Note: PropertyId should likely be Property_id for consistency.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    House_name = models.CharField(max_length=30)
    PropertyId = models.IntegerField()
    Location = models.TextField(blank=True, null=True)
    category_choices = (
        ('House', 'house'),
        ('Sublet', 'sublet'),
        ('Hostel', 'hostel')
    )
    category = models.CharField(max_length=30, choices=category_choices)
    BedRoom = models.IntegerField()
    BathRoom = models.IntegerField()
    Belcony = models.IntegerField()
    Price = models.IntegerField()
    Availability = models.DateField()
    Description = models.TextField(blank=True, null=True)
    image1 = models.ImageField(upload_to='properties/')
    image2 = models.ImageField(upload_to='properties/')
    image3 = models.ImageField(upload_to='properties/')
    def __str__(self):
        return self.House_name

# Model for available houses
class AvailableHouse(models.Model):
    """
    Stores details of houses available for booking.
    - Includes house name, property ID, location, category, price, availability, and up to three images.
    - Note: Overlaps with HouseOwner; consider consolidating or clarifying roles.
    """
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

# Model for tenants
class Tenant(models.Model):
    """
    Represents a tenant user.
    - One-to-one relationship with CustomUser.
    - Currently minimal; can be extended with tenant-specific fields.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

# Model for booking requests
class BookingRequest(models.Model):
    """
    Stores booking requests for houses.
    - Links a tenant to an AvailableHouse.
    - Tracks request date and status (Pending by default).
    """
    house = models.ForeignKey(AvailableHouse, on_delete=models.CASCADE)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    date_requested = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Pending')
    def __str__(self):
        return f"{self.tenant.user.username} - {self.house.House_name}"

# Model for food suppliers and their offerings
class FoodSupplier(models.Model):
    """
    Stores food items listed by food suppliers.
    - One-to-one relationship with CustomUser.
    - Includes food ID, name, location, category (veg/non-veg), price, and description.
    - Note: Price and FoodId are unique and optional, which may cause issues; review constraints.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    FoodId = models.IntegerField(null=True, blank=True, unique=True)
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

# Model for available food items
class AvailableFoods(models.Model):
    """
    Stores food items available for ordering.
    - Linked to a FoodSupplier via ForeignKey.
    - Includes name, location, details, image, duration, meals per day, and price.
    - Note: Price, duration, and meals_per_day are CharFields, which may complicate calculations.
    """
    supplier = models.ForeignKey(FoodSupplier, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    details = models.TextField()
    image = models.ImageField(upload_to='foods/')
    duration = models.CharField(max_length=100, blank=True)
    meals_per_day = models.CharField(max_length=100, blank=True)
    price = models.CharField(max_length=100, blank=True)
    def __str__(self):
        return self.name

# Model for food orders
class Order(models.Model):
    """
    Stores customer food orders.
    - Links to CustomUser (customer) and AvailableFoods (food item).
    - Includes order ID, items (as text), time, status, and creation timestamp.
    - Status options: Pending, Accepted, Declined.
    """
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

# Model for bills associated with orders
class Bill(models.Model):
    """
    Stores billing information for orders.
    - Linked to an Order via ForeignKey.
    - Includes amount, creation timestamp, and status (Pending, Paid, Overdue).
    """
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

# Model for customer complaints
class Complaint(models.Model):
    """
    Stores customer complaints related to orders.
    - Linked to CustomUser (customer) and optionally to an Order.
    - Includes description, status (Open, Resolved, Closed), and creation timestamp.
    """
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