from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views  # Imported auth views for login/logout
from . import views
from .admin import custom_admin_site  # Import custom admin site


urlpatterns = [
    # Custom Admin Site
    path('admin/', custom_admin_site.urls), 

    # Home and static pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),

    # Contact and FAQ
    path('contact/', views.contact, name='contact'),
    path('contact/success/', views.contact_success, name='contact_success'), 
    path('Faq/', views.faq, name='Faq'),  

    # Veterinary directory and review submission (for regular users)
    path('Directory/', views.veterinary_directory, name='Directory'),  
    path('Submit_review/<int:clinic_id>/', views.submit_review, name='Submit_review'),

    # Authentication (Login, Logout, Register, Profile)
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),  
    path('register/', views.register, name='register'),

    # User Dashboard
    path('dashboard/', views.user_dashboard, name='user_dashboard'),

    # Admin Dashboard
    path('admin/dashboard/', views.admin_dashboard, name='Admin_dashboard'),

    # Admin-specific URLs for Veterinary Directory Management
    path('admin-directory/', views.veterinary_directory, name='admin_directory'),
    path('admin-directory/add/', views.add_clinic, name='Add_clinic'),
    path('admin-directory/edit/<int:clinic_id>/', views.edit_clinic, name='Edit_clinic'),
    path('admin-directory/delete/<int:clinic_id>/', views.delete_clinic, name='Confirm_delete_clinic'),

    # FAQ Management (Admin)
    path('custom-admin/faq/add/', views.add_faq, name='add_faq'),
    path('custom-admin/faq/edit/<int:faq_id>/', views.edit_faq, name='edit_faq'),
    path('custom-admin/faq/delete/<int:faq_id>/', views.delete_faq, name='confirm_delete_faq'),

    # Report Generation & Download (Admin)
    path('generate_contact_us_report/', views.generate_report, name='generate_contact_us_report'),
    path('admin/download_report/<int:report_id>/', views.download_report, name='download_report'),

    # Pet Care Tips Management (Admin)
    path('pet-care-tips/', views.pet_care_tips, name='pet_care_tips'),
    path('pet-care-tips/add/', views.add_pet_care_tip, name='add_pet_care_tip'),
    path('pet-care-tips/edit/<int:tip_id>/', views.edit_pet_care_tip, name='edit_pet_care_tip'),
    path('pet-care-tips/delete/<int:tip_id>/', views.delete_pet_care_tip, name='delete_pet_care_tip'),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
