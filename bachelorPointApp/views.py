# Django imports
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.urls import reverse
from django.contrib.auth import authenticate, login

# App models and forms
from .models import (
    AvailableFoods, FoodSupplier, AvailableHouse, HouseOwner, BookingRequest,
    Order, Bill, Complaint, CustomUser, EmailOTP, Profile, Tenant
)
from .forms import CustomUserRegistrationForm, LoginForm, AvailableFoodsForm, HouseOwnerForm

import random
import string

# ==================== Static Pages ====================

def Home(request):
    """Render the Home page."""
    return render(request, template_name='htmlPages/Home.html')

def AboutUs(request):
    """Render the About Us page."""
    return render(request, template_name='htmlPages/AboutUs.html')

def ContactUs(request):
    """Render the Contact Us page."""
    return render(request, template_name='htmlPages/ContactUs.html')

def UserDetailsPage(request):
    """Render the User Details page (view-only page)."""
    return render(request, template_name='htmlPages/UserDetailsPage.html')

# ==================== Landing Pages ====================

def BachelorLandingPage(request):
    """
    Render the landing page for bachelors with all available foods and houses.
    """
    foods = AvailableFoods.objects.all()
    houses = AvailableHouse.objects.all()
    return render(request, 'htmlPages/BachelorLandingPage.html', {'foods': foods, 'houses': houses})

@login_required
def FoodSupplierLandingPage(request, section='orders'):
    """
    Render the landing page for food suppliers, sectioned by orders, bills, complaints, add-food, delete-food.
    """
    if request.user.user_type != 'food_supplier':
        return redirect('Home')

    context = {}

    # Section: View Orders
    if section == 'orders':
        orders = Order.objects.filter(food__supplier__user=request.user).order_by('-created_at')
        context = {'orders': orders, 'section': 'orders'}

    # Section: View Bills
    elif section == 'bills':
        bills = Bill.objects.filter(order__food__in=AvailableFoods.objects.all()).order_by('-created_at')
        context = {'bills': bills, 'section': 'bills'}

    # Section: View Complaints
    elif section == 'complaints':
        complaints = Complaint.objects.filter(order__food__in=AvailableFoods.objects.all()).order_by('-created_at')
        context = {'complaints': complaints, 'section': 'complaints'}

    # Section: Add New Food
    elif section == 'add-food':
        form = AvailableFoodsForm()
        if request.method == 'POST':
            form = AvailableFoodsForm(request.POST, request.FILES)
            if form.is_valid():
                supplier, _ = FoodSupplier.objects.get_or_create(user=request.user)
                food_item = form.save(commit=False)
                food_item.supplier = supplier
                food_item.save()
                messages.success(request, 'Food item added successfully and will be visible to bachelors.')
                return redirect('FoodSupplierLandingPageSection', section='orders')
            else:
                messages.error(request, 'Please fill all required fields correctly.')
        context = {'section': 'add-food', 'form': form}

    # Section: Delete Food
    elif section == 'delete-food':
        supplier, _ = FoodSupplier.objects.get_or_create(user=request.user)
        foods = AvailableFoods.objects.filter(supplier=supplier)
        if request.method == 'POST':
            food_id = request.POST.get('food_id')
            if not food_id or not food_id.isdigit():
                messages.error(request, 'Invalid food ID.')
                return redirect('FoodSupplierLandingPageSection', section='delete-food')
            if not AvailableFoods.objects.filter(id=food_id, supplier=supplier).exists():
                messages.error(request, 'Food item not found or you do not have permission to delete it.')
                return redirect('FoodSupplierLandingPageSection', section='delete-food')
            AvailableFoods.objects.get(id=food_id, supplier=supplier).delete()
            messages.success(request, 'Food item deleted successfully.')
            return redirect('FoodSupplierLandingPageSection', section='delete-food')
        context = {'foods': foods, 'section': 'delete-food'}

    return render(request, 'htmlPages/FoodSupplierLandingPage.html', context)

@login_required
def HouseOwnerLandingPage(request, section='bookings'):
    """
    Render the landing page for house owners with multiple sections:
    bookings, listings, add-house, delete-house, complaints.
    """
    if request.user.user_type != 'house_owner':
        return redirect('Home')

    houses = HouseOwner.objects.filter(user=request.user)
    context = {'houses': houses}

    # Section: View Booking Requests
    if section == 'bookings':
        booking_requests = BookingRequest.objects.all().order_by('-date_requested')
        context.update({'booking_requests': booking_requests, 'section': 'bookings'})

    # Section: Show Listings
    elif section == 'listings':
        context.update({'section': 'listings'})

    # Section: Add New House
    elif section == 'add-house':
        form = HouseOwnerForm()
        if request.method == 'POST':
            form = HouseOwnerForm(request.POST, request.FILES)
            if form.is_valid():
                house = form.save(commit=False)
                house.user = request.user
                house.save()
                messages.success(request, 'House added successfully and is now visible to bachelors.')
                return redirect(reverse('HouseOwnerLandingPageSection', kwargs={'section': 'listings'}))
            else:
                messages.error(request, 'Please fill all required fields correctly.')
        context.update({'form': form, 'section': 'add-house'})

    # Section: Delete House
    elif section == 'delete-house':
        if request.method == 'POST':
            house_id = request.POST.get('house_id')
            if not house_id or not house_id.isdigit():
                messages.error(request, 'Invalid house ID.')
                return redirect(reverse('HouseOwnerLandingPageSection', kwargs={'section': 'delete-house'}))
            if not HouseOwner.objects.filter(id=house_id, user=request.user).exists():
                messages.error(request, 'House not found or you do not have permission to delete it.')
                return redirect(reverse('HouseOwnerLandingPageSection', kwargs={'section': 'delete-house'}))
            house = HouseOwner.objects.get(id=house_id, user=request.user)
            AvailableHouse.objects.filter(Property_id=house.PropertyId).delete()
            house.delete()
            messages.success(request, 'House deleted successfully.')
            return redirect(reverse('HouseOwnerLandingPageSection', kwargs={'section': 'delete-house'}))
        context.update({'section': 'delete-house'})

    elif section == 'complaints':
        context.update({'section': 'complaints'})

    # Handle Accept/Decline Booking Requests
    if request.method == 'POST' and 'request_id' in request.POST:
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')
        if request_id and action:
            booking_request = get_object_or_404(BookingRequest, id=request_id)
            booking_request.status = 'Accepted' if action == 'accept' else 'Declined'
            booking_request.save()
            messages.success(request, f'Request #{request_id} has been {booking_request.status.lower()}.')
            return redirect(reverse('HouseOwnerLandingPageSection', kwargs={'section': 'bookings'}))

    return render(request, 'htmlPages/HouseOwnerLandingPage.html', context)

# ==================== Profile & Authentication ====================

@login_required
def ProfilePage(request):
    """
    Render and update the user's profile page.
    """
    profile = request.user.profile
    if request.method == 'POST':
        # Update fields
        profile.name = request.POST.get('name')
        profile.mobile = request.POST.get('mobile')
        profile.gender = request.POST.get('gender')
        profile.dob = request.POST.get('dob')
        profile.profession = request.POST.get('profession')
        profile.address = request.POST.get('address')
        profile.blood_group = request.POST.get('blood_group')
        # Handle profile image
        if 'image' in request.FILES:
            if profile.image:
                profile.image.delete(save=False)
            profile.image = request.FILES['image']
        elif request.POST.get('image_changed') == 'true':
            if profile.image:
                profile.image.delete(save=False)
            profile.image = None
        profile.save()
        return redirect('ProfilePage')
    return render(request, 'htmlPages/ProfilePage.html', {'profile': profile})

def Register(request):
    """
    Handle user registration and send OTP to verify email.
    """
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            send_otp_email(user)
            request.session['user_id'] = user.id
            return redirect('VerifyEmailPage')
    else:
        form = CustomUserRegistrationForm()
    return render(request, 'htmlPages/Register.html', {'form': form})

def send_otp_email(user):
    """Generate OTP and send it via email to the user."""
    otp = str(random.randint(100000, 999999))
    EmailOTP.objects.update_or_create(user=user, defaults={'otp': otp})
    send_mail(
        subject='Your OTP Code',
        message=f'Your OTP is {otp}',
        from_email='noreply@bachelorpoint.com',
        recipient_list=[user.email],
        fail_silently=False,
    )

def VerifyEmailPage(request):
    """
    Handle OTP verification for email.
    """
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('Register')
    user = CustomUser.objects.get(id=user_id)

    if request.method == 'POST':
        if 'resend_otp' in request.POST:
            send_otp_email(user)
            messages.success(request, 'A new OTP has been sent to your email.')
            return redirect('VerifyEmailPage')
        else:
            entered_otp = request.POST.get('otp')
            otp_obj = EmailOTP.objects.filter(user=user).first()
            if otp_obj and otp_obj.otp == entered_otp:
                user.is_active = True
                user.save()
                otp_obj.delete()
                login(request, user)
                return redirect_user_by_type(user)
            else:
                messages.error(request, 'Invalid OTP. Please try again.')

    return render(request, 'htmlPages/VerifyEmailPage.html', {'email': user.email})

def LogIn(request):
    """
    Handle user login using Django's authentication system.
    """
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect_user_by_type(user)
    else:
        form = LoginForm()
    return render(request, 'htmlPages/LogIn.html', {'form': form})

def redirect_user_by_type(user):
    """
    Redirect user to appropriate landing page based on their user type.
    """
    if user.user_type == 'bachelor':
        return redirect('BachelorLandingPage')
    elif user.user_type == 'food_supplier':
        return redirect('FoodSupplierLandingPage')
    elif user.user_type == 'house_owner':
        return redirect('HouseOwnerLandingPage')
    else:
        return redirect('Home')

# ==================== Order & Details ====================

def FoodDetails(request, food_id):
    """
    Show food details and handle order placement.
    """
    food = get_object_or_404(AvailableFoods, id=food_id)
    if request.method == 'POST':
        quantity = request.POST.get('quantity')
        if quantity and quantity.isdigit() and int(quantity) > 0:
            quantity = int(quantity)
            total_price = food.price * quantity
            # Generate unique order ID
            while True:
                order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                if not Order.objects.filter(order_id=order_id).exists():
                    break
            Order.objects.create(
                customer=request.user,
                food=food,
                order_id=order_id,
                items=f"{food.name} (Quantity: {quantity}, Total Price: ${total_price})",
                status='Pending'
            )
            messages.success(request, 'Order placed successfully. Awaiting supplier confirmation.')
            return redirect('BachelorLandingPage')
        else:
            messages.error(request, 'Please enter a valid quantity.')
    context = {'food': food}
    return render(request, 'htmlPages/FoodDetails.html', context)

def update_order_status(request, order_id):
    """
    Allow suppliers to accept or decline an order.
    """
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id, food__supplier__user=request.user)
        action = request.POST.get('action')
        if action == 'accept':
            order.status = 'Accepted'
        elif action == 'decline':
            order.status = 'Declined'
        order.save()
        messages.success(request, f'Order #{order.order_id} {action}ed successfully.')
        return redirect('FoodSupplierLandingPageSection', section='orders')
    return redirect('FoodSupplierLandingPageSection', section='orders')

def HouseDetailsPage(request, property_id):
    """
    Show house details to bachelor users.
    """
    house = get_object_or_404(AvailableHouse, Property_id=property_id)
    if request.method == 'POST':
        tenant, created = Tenant.objects.get_or_create(user=request.user)
        return redirect(reverse('BachelorLandingPage'))
    return render(request, 'htmlPages/HouseDetailsPage.html', {'house': house})
