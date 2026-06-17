from django import forms
from .models import Inquiry

class InquiryForm(forms.ModelForm):
    state = forms.CharField(max_length=100, required=False)
    lga = forms.CharField(max_length=100, required=False)

    class Meta:
        model = Inquiry
        fields = [
            'customer_name', 'email', 'country', 'phone', 
            'state', 'lga', 'city', 'full_address', 'message'
        ]
