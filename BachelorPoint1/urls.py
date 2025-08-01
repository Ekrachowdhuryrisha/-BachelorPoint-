from django.contrib import admin                                              # Import Django admin module
from django.urls import path                                                 # Import path function for URL routing
from bachelorPointApp import views as b_views                                # Import views from bachelorPointApp with alias
from django.conf import settings                                             # Import Django settings
from django.conf.urls.static import static                                   # Import static for serving media files

urlpatterns = [                                                              # List of URL patterns
    path('admin/', admin.site.urls),                                         # Admin panel URL
    path('', b_views.Home, name='Home'),                                     # Homepage URL
    path('LogIn/', b_views.LogIn, name='LogIn'),                             # Login page URL
    path('AboutUs/', b_views.AboutUs, name='AboutUs'),                       # About Us page URL
    path('BachelorLandingPage/', b_views.BachelorLandingPage, name='BachelorLandingPage'),  # Bachelor landing page URL
    path('ContactUs/', b_views.ContactUs, name='ContactUs'),                 # Contact Us page URL
    path('ProfilePage/', b_views.ProfilePage, name='ProfilePage'),           # User profile page URL
    path('FoodDetails/<int:food_id>/', b_views.FoodDetails, name='FoodDetails'),  # Food details page with food ID parameter
    path('FoodSupplierLandingPage/', b_views.FoodSupplierLandingPage, name='FoodSupplierLandingPage'),  # Food supplier landing page URL
    path('update-order/<int:order_id>/', b_views.update_order_status, name='update_order_status'),  # Update order status with order ID
    path('FoodSupplierLandingPageSection/<str:section>/', b_views.FoodSupplierLandingPage, name='FoodSupplierLandingPageSection'),  # Food supplier section page with section parameter
    path('HouseDetailsPage/<str:property_id>/', b_views.HouseDetailsPage, name='HouseDetailsPage'),  # House details page with property ID
    path('HouseOwnerLandingPage/', b_views.HouseOwnerLandingPage, name='HouseOwnerLandingPage'),  # House owner landing page URL
    path('HouseOwnerLandingPage/<str:section>/', b_views.HouseOwnerLandingPage, name='HouseOwnerLandingPageSection'),  # House owner section page with section parameter
    path('Register/', b_views.Register, name='Register'),                    # Registration page URL
    path('UserDetailsPage/', b_views.UserDetailsPage, name='UserDetailsPage'),  # User details page URL
    path('activate/<uidb64>/<token>/', b_views.VerifyEmailPage, name='activate'),  # Email activation URL with user ID and token
    path('VerifyEmailPage/', b_views.VerifyEmailPage, name='VerifyEmailPage'),  # Email verification page URL
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)             # Serve media files in development