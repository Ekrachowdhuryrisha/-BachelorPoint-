from django.contrib import admin
from .models import Register, LogIn, Profile, HouseOwner, FoodSupplier, AvailableHouse, AvailableFoods, BookingRequest, Tenant
from django.contrib.auth.models import User

# Register your models here.

admin.site.register(Register)
admin.site.register(LogIn)
admin.site.register(Profile)
admin.site.register(HouseOwner)
admin.site.register(FoodSupplier)
admin.site.register(AvailableHouse)
admin.site.register(AvailableFoods)
admin.site.register(BookingRequest)
admin.site.register(Tenant)
