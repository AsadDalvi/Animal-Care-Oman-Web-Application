from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm, UserChangeForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.admin.views.decorators import staff_member_required
from .models import (
    Clinic, Review, FAQ, Message, ClinicReview,
    ContactMessage, ContactUsMessage, Report, PetCareTip
)
from .forms import ClinicReviewForm, ContactForm, ClinicForm, FAQForm, PetCareTipForm
import csv
from django.contrib.auth.models import User



# Home page view
def home(request):
    return render(request, 'home.html')


# About page view
def about(request):
    return render(request, 'about.html')



def profile_view(request):
    # Render the profile page template
    return render(request, 'accounts/profile.html')



@login_required
def generate_report(request):
    # Fetch all contact messages
    contact_messages = ContactMessage.objects.all()

    # Generate report content
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="contact_messages_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Email', 'Message', 'Sent At'])

    for message in contact_messages:
        writer.writerow([message.name, message.email, message.message, message.sent_at])

    # Store report metadata in the database
    report = Report.objects.create(
        report_type="Contact Messages",
        content="Generated contact messages report",
        generated_by=request.user  # Stores which admin user generated the report
    )
    report.save()

    return response


# Contact page view
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save the contact message
            contact_message = ContactMessage.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                message=form.cleaned_data['message']
            )
            
            # Create a report for the admin
            report = Report(
                report_type='Contact Message',
                content=f"Message from {form.cleaned_data['name']} ({form.cleaned_data['email']}): {form.cleaned_data['message']}",
                generated_by=User.objects.first(),  
            )
            report.save()

            # Show a success message
            messages.success(request, "Your message has been sent successfully!")

            # Redirect to the success page
            return redirect('contact_success')
    else:
        form = ContactForm()

    return render(request, 'core/contact.html', {'form': form})


# Define the success page view
def contact_success(request):
    return render(request, 'core/contact_success.html')


# FAQ page view
def faq(request):
    faqs = FAQ.objects.all()
    return render(request, 'Faq.html', {'faqs': faqs})



# Admin-only Views for FAQ Management
# Add new FAQ view (Admin only)
@staff_member_required
def add_faq(request):
    if request.method == 'POST':
        form = FAQForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('Faq')  # Redirect to the FAQ page after adding
    else:
        form = FAQForm()
    return render(request, 'add_faq.html', {'form': form})


# Edit existing FAQ view (Admin only)
@staff_member_required
def edit_faq(request, faq_id):
    faq = get_object_or_404(FAQ, id=faq_id)
    
    if request.method == 'POST':
        form = FAQForm(request.POST, instance=faq)
        if form.is_valid():
            form.save()
            return redirect('Faq')  # Redirect to the FAQ page after editing
    else:
        form = FAQForm(instance=faq)
    
    return render(request, 'edit_faq.html', {'form': form, 'faq': faq})

# Delete FAQ view (Admin only)
@staff_member_required
def delete_faq(request, faq_id):
    faq = get_object_or_404(FAQ, id=faq_id)
    
    if request.method == 'POST':
        faq.delete()
        return redirect('Faq')  # Redirect to the FAQ page after deletion
    
    return render(request, 'confirm_delete_faq.html', {'faq': faq})


def dashboard_view(request):
    return render(request, 'admin/Admin_dashboard.html')



def veterinary_directory(request):
    query = request.GET.get('q')  # Get the search query from the GET request
    if query:
        clinics = Clinic.objects.filter(name__icontains=query)  # Filter clinics by name
    else:
        clinics = Clinic.objects.all()  # If no search query, show all clinics

    return render(request, 'Directory.html', {'clinics': clinics})


# Submit review page view for clinic
@login_required
def submit_review(request, clinic_id):
    clinic = get_object_or_404(Clinic, id=clinic_id)  # Get the specific clinic by ID

    if request.method == 'POST':
        form = ClinicReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.clinic = clinic 
            review.user = request.user  
            review.save()
            messages.success(request, "Review submitted successfully!")
            return redirect('Directory')  # Redirect to Directory.html
        else:
            messages.error(request, "Error submitting review. Please try again.")
    else:
        form = ClinicReviewForm()

    # Pass the specific clinic object to the template
    return render(request, 'Submit_review.html', {'clinic': clinic, 'form': form})



# User registration view
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(request, 'register.html', {'form': form})



# Admin dashboard view
@staff_member_required
def admin_dashboard(request):
    contact_messages = ContactMessage.objects.all()
    total_clinic_reviews = Review.objects.count()
    total_pet_care_tips = PetCareTip.objects.count()
    reports = Report.objects.all()

    return render(request, 'Admin_dashboard.html', {
        'contact_messages': contact_messages,
        'total_clinic_reviews': total_clinic_reviews,
        'total_pet_care_tips': total_pet_care_tips,
        'reports': reports,
    })


# Add clinic view (Admin only)
def add_clinic(request):
    if not request.user.is_staff:  # Only admin users can access
        return redirect('home')
    
    if request.method == 'POST':
        form = ClinicForm(request.POST, request.FILES)  # Handles form data and image files
        if form.is_valid():
            form.save()  # Saves the new clinic to the database
            return redirect('Directory')  # Redirect to the clinic directory after adding
    else:
        form = ClinicForm()

    return render(request, 'Add_clinic.html', {'form': form})


# Edit clinic view (Admin only)
def edit_clinic(request, clinic_id):
    if not request.user.is_staff:  # Only admin users can access
        return redirect('home')
    
    clinic = get_object_or_404(Clinic, id=clinic_id)
    
    if request.method == 'POST':
        form = ClinicForm(request.POST, request.FILES, instance=clinic)
        if form.is_valid():
            form.save()
            return redirect('Directory')  # Redirect to the clinic directory after editing
    else:
        form = ClinicForm(instance=clinic)
    
    return render(request, 'Edit_clinic.html', {'form': form, 'clinic': clinic})


# Delete clinic view (Admin only)
def delete_clinic(request, clinic_id):
    if not request.user.is_staff:  # Only admin users can access
        return redirect('home')

    clinic = get_object_or_404(Clinic, id=clinic_id)

    if request.method == 'POST':
        clinic.delete()
        return redirect('Directory')  # Redirect to the clinic directory after deletion

    return render(request, 'Confirm_delete_clinic.html', {'clinic': clinic})


# User dashboard view
@login_required
def user_dashboard(request):
    clinic_reviews = ClinicReview.objects.filter(user=request.user)
    contact_messages = Message.objects.filter(user=request.user)

    # No need to check for 'profile' anymore since it was removed
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        if username:
            request.user.username = username
        if email:
            request.user.email = email
        request.user.save()

    return render(request, 'user_dashboard.html', {
        'clinic_reviews': clinic_reviews,
        'contact_messages': contact_messages
    })



# Pet Care Tip views (Admin only)
# Display all pet care tips or filtered results based on search
def pet_care_tips(request):
    search_query = request.GET.get('search', '')  # Get search query from GET request
    
    # If there's a search query, filter the tips by title or content
    if search_query:
        tips = PetCareTip.objects.filter(title__icontains=search_query) | PetCareTip.objects.filter(content__icontains=search_query)
    else:
        tips = PetCareTip.objects.all()  # If no search query, show all tips
    
    return render(request, 'pet_care_tips.html', {'tips': tips})


@staff_member_required
def add_pet_care_tip(request):
    if request.method == 'POST':
        form = PetCareTipForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pet_care_tips')
    else:
        form = PetCareTipForm()

    return render(request, 'add_pet_care_tip.html', {'form': form})


@staff_member_required
def edit_pet_care_tip(request, tip_id):
    tip = get_object_or_404(PetCareTip, id=tip_id)

    if request.method == 'POST':
        form = PetCareTipForm(request.POST, instance=tip)
        if form.is_valid():
            form.save()
            return redirect('pet_care_tips')  # Redirect back to the list of tips
    else:
        form = PetCareTipForm(instance=tip)

    return render(request, 'edit_pet_care_tip.html', {'form': form})


@staff_member_required
def delete_pet_care_tip(request, tip_id):
    tip = get_object_or_404(PetCareTip, id=tip_id)
    
    if request.method == 'POST':
        tip.delete()
        return redirect('pet_care_tips')  # Redirect back to the list of tips

    return render(request, 'confirm_delete_pet_care_tip.html', {'tip': tip})


# Download and report generation views for Admin
@staff_member_required
def generate_contact_us_report(request):
    if request.method == "POST":
        # Get all contact messages
        messages = ContactUsMessage.objects.all()

        # Create CSV file content for the report
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="contact_us_report.csv"'

        writer = csv.writer(response)
        writer.writerow(['Name', 'Email', 'Subject', 'Message', 'Sent At'])

        for msg in messages:
            writer.writerow([msg.name, msg.email, msg.subject, msg.message, msg.sent_at])

        # Optionally, create a record in the Report model
        report_content = "\n".join([f"{msg.name} | {msg.email} | {msg.subject} | {msg.message} | {msg.sent_at}" for msg in messages])
        Report.objects.create(
            report_type="Contact Us Messages",
            content=report_content,
            generated_by=request.user
        )

        return response

    # Optional: Render a page if GET request is made
    return render(request, 'generate_contact_us_report.html')


@staff_member_required
def download_report(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    response = HttpResponse(report.content, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="{report.report_type}_{report.id}.txt"'
    return response