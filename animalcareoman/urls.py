from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from core import views  # Import views from core app

urlpatterns = [
    # Home page route
    path('', views.home, name='home'),  # Home path to view the home page

    # Admin page route
    path('admin/', admin.site.urls),  # Standard Django admin

    path('core/', include('core.urls')),  # Include the URLs defined in core.urls

    # Authentication (Login, Logout, Register)
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),

    # Contact Pages
    path('contact/', views.contact, name='contact'),
    path('contact/success/', views.contact_success, name='contact_success'),

    # User Dashboard (Now direct)
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
