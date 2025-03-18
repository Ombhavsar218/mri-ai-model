from django import forms
from .models import Registration

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
