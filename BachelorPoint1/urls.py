from django.contrib import admin
from django.urls import path
from bachelorPointApp import views as b_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', b_views.Home, name='Home'),
    path('LogIn/', b_views.LogIn, name='LogIn'),
    path('AboutUs/', b_views.AboutUs, name='AboutUs'),
    path('BachelorLandingPage/', b_views.BachelorLandingPage, name='BachelorLandingPage'),
    path('ContactUs/', b_views.ContactUs, name='ContactUs'),
    path('ProfilePage/', b_views.ProfilePage, name='ProfilePage'),
    path('FoodDetails/<int:food_id>/', b_views.FoodDetails, name='FoodDetails'),
    path('FoodSupplierLandingPage/', b_views.FoodSupplierLandingPage, name='FoodSupplierLandingPage'),
    path('update-order/<int:order_id>/', b_views.update_order_status, name='update_order_status'),
    path('FoodSupplierLandingPage/<str:section>/', b_views.FoodSupplierLandingPage, name='FoodSupplierLandingPageSection'),
    path('HouseDetailsPage/<str:property_id>/', b_views.HouseDetailsPage, name='HouseDetailsPage'),
    path('HouseOwnerLandingPage/', b_views.HouseOwnerLandingPage, name='HouseOwnerLandingPage'),
    path('HouseOwnerLandingPage/<str:section>/', b_views.HouseOwnerLandingPage, name='HouseOwnerLandingPageSection'),
    path('Register/', b_views.Register, name='Register'),
    path('UserDetailsPage/', b_views.UserDetailsPage, name='UserDetailsPage'),
    path('activate/<uidb64>/<token>/', b_views.VerifyEmailPage, name='activate'),
    path('VerifyEmailPage/', b_views.VerifyEmailPage, name='VerifyEmailPage'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)