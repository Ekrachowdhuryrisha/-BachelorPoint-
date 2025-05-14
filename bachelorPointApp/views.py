from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import AvailableFoods, FoodSupplier, AvailableHouse, HouseOwner, BookingRequest, Order, Bill, Complaint, CustomUser, EmailOTP, Profile, Tenant
from .forms import CustomUserRegistrationForm, LoginForm, AvailableFoodsForm, HouseOwnerForm
import random
import string
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.tokens import default_token_generator

def Home(request):
    return render(request, template_name='htmlPages/Home.html')

def AboutUs(request):
    return render(request, template_name='htmlPages/AboutUs.html')

def BachelorLandingPage(request):
    foods = AvailableFoods.objects.all()
    houses = AvailableHouse.objects.all()
    return render(request, 'htmlPages/BachelorLandingPage.html', {'foods': foods, 'houses': houses})

def ContactUs(request):
    return render(request, template_name='htmlPages/ContactUs.html')

def FoodSupplierLandingPage(request, section='orders'):
    if request.user.user_type != 'food_supplier':
        return redirect('Home')
    
    context = {}
    if section == 'orders':
        orders = Order.objects.filter(food__supplier__user=request.user).order_by('-created_at')
        context = {'orders': orders, 'section': 'orders'}
    elif section == 'bills':
        bills = Bill.objects.filter(order__food__in=AvailableFoods.objects.all()).order_by('-created_at')
        context = {'bills': bills, 'section': 'bills'}
    elif section == 'complaints':
        complaints = Complaint.objects.filter(order__food__in=AvailableFoods.objects.all()).order_by('-created_at')
        context = {'complaints': complaints, 'section': 'complaints'}
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
            food = AvailableFoods.objects.get(id=food_id, supplier=supplier)
            food.delete()
            messages.success(request, 'Food item deleted successfully.')
            return redirect('FoodSupplierLandingPageSection', section='delete-food')
        context = {'foods': foods, 'section': 'delete-food'}
    
    return render(request, 'htmlPages/FoodSupplierLandingPage.html', context)

def HouseDetailsPage(request, property_id):
    house = get_object_or_404(AvailableHouse, Property_id=property_id)
    if request.method == 'POST':
        tenant, created = Tenant.objects.get_or_create(user=request.user)
        booking = BookingRequest.objects.create(house=house, tenant=tenant)
        return redirect(reverse('HouseOwnerLandingPage'))
    return render(request, 'htmlPages/HouseDetailsPage.html', {'house': house})

@login_required
def HouseOwnerLandingPage(request, section='bookings'):
    if request.user.user_type != 'house_owner':
        return redirect('Home')

    houses = HouseOwner.objects.filter(user=request.user)
    context = {'houses': houses}

    if section == 'bookings':
        booking_requests = BookingRequest.objects.all().order_by('-date_requested')
        context.update({'booking_requests': booking_requests, 'section': 'bookings'})
    elif section == 'listings':
        context.update({'section': 'listings'})
    elif section == 'add-house':
        form = HouseOwnerForm()
        if request.method == 'POST':
            form = HouseOwnerForm(request.POST, request.FILES)
            if form.is_valid():
                house = form.save(commit=False)
                house.user = request.user
                house.save()
                available_house = AvailableHouse.objects.create(
                    House_name=house.House_name,
                    Property_id=house.PropertyId,
                    Location=house.Location,
                    Category=house.category,
                    Price=house.Price,
                    Availability=house.Availability,
                    image1=house.image1,
                    image2=house.image2,
                    image3=house.image3
                )
                messages.success(request, 'House added successfully and is now visible to bachelors.')
                return redirect(reverse('HouseOwnerLandingPageSection', kwargs={'section': 'listings'}))
            else:
                messages.error(request, 'Please fill all required fields correctly.')
        context.update({'form': form, 'section': 'add-house'})
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

    if request.method == 'POST' and 'request_id' in request.POST:
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')
        if request_id and action:
            booking_request = get_object_or_404(BookingRequest, id=request_id)
            if action == 'accept':
                booking_request.status = 'Accepted'
                messages.success(request, f'Request #{request_id} has been accepted.')
            elif action == 'decline':
                booking_request.status = 'Declined'
                messages.success(request, f'Request #{request_id} has been declined.')
            booking_request.save()
            return redirect(reverse('HouseOwnerLandingPageSection', kwargs={'section': 'bookings'}))

    return render(request, 'htmlPages/HouseOwnerLandingPage.html', context)

def UserDetailsPage(request):
    return render(request, template_name='htmlPages/UserDetailsPage.html')
    

def UserDetailsPage(request):
    return render(request, template_name='htmlPages/UserDetailsPage.html')

@login_required
def ProfilePage(request):
    profile = request.user.profile
    if request.method == 'POST':
        profile.name = request.POST.get('name')
        profile.mobile = request.POST.get('mobile')
        profile.gender = request.POST.get('gender')
        profile.dob = request.POST.get('dob')
        profile.profession = request.POST.get('profession')
        profile.address = request.POST.get('address')
        profile.blood_group = request.POST.get('blood_group')
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
    if user.user_type == 'bachelor':
        return redirect('BachelorLandingPage')
    elif user.user_type == 'food_supplier':
        return redirect('FoodSupplierLandingPage')
    elif user.user_type == 'house_owner':
        return redirect('HouseOwnerLandingPage')
    else:
        return redirect('Home')


def FoodDetails(request, food_id):
    food = get_object_or_404(AvailableFoods, id=food_id)
    if request.method == 'POST':
        quantity = request.POST.get('quantity')
        if quantity and quantity.isdigit() and int(quantity) > 0:
            while True:
                order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                if not Order.objects.filter(order_id=order_id).exists():
                    break
            Order.objects.create(
                customer=request.user,
                food=food,
                order_id=order_id,
                items=f"{food.name} (Quantity: {quantity})",
                status='Pending'
            )
            messages.success(request, 'Order placed successfully. Awaiting supplier confirmation.')
            return redirect('BachelorLandingPage')
        else:
            messages.error(request, 'Please enter a valid quantity.')
    context = {'food': food}
    return render(request, 'htmlPages/FoodDetails.html', context)

def update_order_status(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id, food__supplier__user=request.user)
        action = request.POST.get('action')
        if action == 'accept':
            order.status = 'Accepted'
        elif action == 'decline':
            order.status = 'Declined'
        order.save()
        messages.success(request, f'Order #{order.order_id} {action}ed successfully.')
        return redirect('FoodSupplierLandingPage', section='orders')
    return redirect('FoodSupplierLandingPage', section='orders')