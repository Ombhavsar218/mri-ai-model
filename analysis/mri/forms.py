from django import forms
from .models import Registration,Expert,MRIRecord
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.core.exceptions import ValidationError

class RegistrationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, label='Password')
    password2 = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')
    
    class Meta:
        model = Registration
        fields = ['username', 'email', 'password1', 'password2']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 != password2:
            raise forms.ValidationError("Passwords do not match")
        
        return cleaned_data

class LoginForm(forms.Form):
    username = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'placeholder': 'Username or Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}), required=True)


class ExpertRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = Expert  # Changed model
        fields = ["username", "email"]

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password1") != cleaned_data.get("password2"):
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

class ExpertLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Email'}), required=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}), required=True)

class RecommendationForm(forms.ModelForm):
    class Meta:
        model = MRIRecord
        fields = ['recommendation', 'precaution']
        widgets = {
            'recommendation': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter recommendation'}),
            'precaution': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter precaution'}),
        }

class CustomPasswordResetForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data['email']
        if not Registration.objects.filter(email=email).exists() and not Expert.objects.filter(email=email).exists():
            raise ValidationError("No account is associated with this email.")
        return email
