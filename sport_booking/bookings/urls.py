from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.views.generic import TemplateView
from .views import UserViewSet, SportFieldViewSet, BookingViewSet 

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('sport-fields', SportFieldViewSet, basename='sportfield')
router.register('bookings', BookingViewSet, basename='booking')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # HTML Pages
    path('login-form/', TemplateView.as_view(template_name='bookings/login_form.html'), name='login_form'),
    path('register-form/', TemplateView.as_view(template_name='bookings/register_form.html'), name='register_form'),
    path('index/', TemplateView.as_view(template_name='bookings/index.html'), name='index'),
    path('my-bookings/', TemplateView.as_view(template_name='bookings/my_bookings.html'), name='my_bookings_page'),
    path('admin-dashboard/', TemplateView.as_view(template_name='bookings/admin_dashboard.html'), name='admin_dashboard'),
    path('sport-field/', TemplateView.as_view(template_name='bookings/sport_field.html'), name='sport_field'),
    path('edit-sport-field/', TemplateView.as_view(template_name='bookings/edit_sport_field.html'), name='edit_sport_field'),
]