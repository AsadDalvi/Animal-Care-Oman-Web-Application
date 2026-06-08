from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.http import HttpResponse
import csv
from .models import Clinic, FAQ, Review, ContactMessage, Report, PetCareTip, Message, ClinicReview


# Custom Admin Dashboard
class CustomAdminSite(admin.AdminSite):
    site_header = "Animal Care Oman Admin"
    site_title = "Admin Dashboard"
    index_title = "Welcome to Animal Care Oman Admin"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view), name="admin_dashboard"),
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        # Fetch necessary data for the dashboard
        contact_messages = ContactMessage.objects.all().order_by('-sent_at')  
        reviews = ClinicReview.objects.all().order_by('-date_submitted')
        total_reviews = reviews.count()
        reports = Report.objects.all().order_by('-generated_at')

        context = {
            'contact_messages': contact_messages, 
            'reviews': reviews,
            'total_reviews': total_reviews,
            'reports': reports,
        }
        return render(request, 'admin/Admin_dashboard.html', context)

custom_admin_site = CustomAdminSite(name='custom_admin')


# Register models with custom admin
@admin.register(Clinic, site=custom_admin_site)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_info', 'address')
    search_fields = ('name', 'contact_info')


@admin.register(FAQ, site=custom_admin_site)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'answer')
    search_fields = ('question',)


@admin.register(Review, site=custom_admin_site)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('clinic', 'user', 'rating')
    list_filter = ('rating',)
    search_fields = ('clinic__name', 'user__username')


# Register ContactMessage and add custom action to generate report
@admin.register(ContactMessage, site=custom_admin_site)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'message', 'sent_at')  # Updated to include sent_at for timings
    search_fields = ('name', 'email', 'subject')

    actions = ['generate_contact_message_report']

    def generate_contact_message_report(self, request, queryset):
        # Check if any messages were selected
        if queryset.exists():
            # Create CSV Excel file report for all contact us messages
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="contact_message_report.csv"'

            # Create CSV writer
            writer = csv.writer(response)
            writer.writerow(['Name', 'Email', 'Subject', 'Message', 'Sent At'])  # Write headers in excel file

            # Write each message to the CSV file
            for msg in queryset:
                writer.writerow([msg.name, msg.email, msg.subject if msg.subject else "No Subject", msg.message, msg.sent_at])

            # store the report in the Report model
            report_content = "\n".join([f"{msg.name} | {msg.email} | {msg.subject if msg.subject else 'No Subject'} | {msg.message} | {msg.sent_at}" for msg in queryset])
            Report.objects.create(
                report_type="Contact Messages",
                content=report_content,
                generated_by=request.user
            )

            return response
        else:
            self.message_user(request, "No messages selected for the report.")
            return None

    # Custom description for the action
    generate_contact_message_report.short_description = "Generate CSV report for selected Contact Messages"


@admin.register(Report, site=custom_admin_site)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('report_type', 'generated_by', 'generated_at')
    search_fields = ('report_type', 'generated_by__username')


@admin.register(PetCareTip, site=custom_admin_site)
class PetCareTipAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title',)
    date_hierarchy = 'created_at'


@admin.register(Message, site=custom_admin_site)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'subject', 'created_at')
    search_fields = ('user__username', 'subject')


@admin.register(ClinicReview, site=custom_admin_site)
class ClinicReviewAdmin(admin.ModelAdmin):
    list_display = ('clinic', 'user', 'rating', 'date_submitted')
    list_filter = ('rating',)
    search_fields = ('clinic__name', 'user__username')