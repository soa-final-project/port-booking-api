from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger Documentation
schema_view = get_schema_view(
    openapi.Info(
        title="Sport Booking API",
        default_version='v1',
        description="API สำหรับระบบจองสนามกีฬา",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@sportbooking.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('bookings.urls')),
    
    # ✅ ลบหรือ comment บรรทัดเหล่านี้ออก เพราะเรามีใน bookings/urls.py แล้ว
    # path('login/', TemplateView.as_view(template_name='login_form.html'), name='login_form'),
    # path('register-form/', TemplateView.as_view(template_name='register_form.html'), name='register_form'),
    
    # Swagger URLs
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# เพิ่ม Media URLs สำหรับ Development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)