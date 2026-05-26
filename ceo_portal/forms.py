from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class CEOSignupForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Required. A valid email address for secure communications and password resets.')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already associated with an account.")
        return email
