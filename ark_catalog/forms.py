from django import forms
from .models import Inquiry

class InquiryForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = [
            'customer_name', 'email', 'country', 'phone', 
            'state', 'lga', 'city', 'full_address', 'message'
        ]
