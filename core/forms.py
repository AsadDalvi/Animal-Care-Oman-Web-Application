from django import forms
from .models import ClinicReview, Clinic, FAQ, PetCareTip

# Form for submitting a review
class ClinicReviewForm(forms.ModelForm):
    # Rating field with 1-5 stars as radio buttons
    rating = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=forms.RadioSelect,
        required=True,
        label='Rating (1 to 5 stars)',
    )

    class Meta:
        model = ClinicReview
        fields = ['rating', 'comment']


# Form for contact page submissions
class ContactForm(forms.Form):
    name = forms.CharField(max_length=255)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)


# Form for Clinic model to add/edit clinic information
class ClinicForm(forms.ModelForm):
    class Meta:
        model = Clinic
        fields = ['name', 'description', 'contact_info', 'address', 'phone_number', 'website', 'location', 'image'] 


# Form for FAQ model to add/edit FAQ information
class FAQForm(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = ['question', 'answer']  


# Form for PetCareTip model to add/edit pet care tips (admin-managed)
class PetCareTipForm(forms.ModelForm):
    class Meta:
        model = PetCareTip
        fields = ['title', 'content'] 
