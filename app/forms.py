from django import forms
from django.contrib.auth.password_validation import validate_password


from .models import CustomUser


class RegistrationUserForm(forms.ModelForm):
    """
    Validation form for user
    """
    class Meta:
        model = CustomUser
        fields = ["email", "contact", "password", "profile_type"]

    def clean_password(self):
        password = self.cleaned_data.get("password")
        validate_password(password)
        return password

class LoginUserForm(forms.Form):
    username = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_password(self):
        password = self.cleaned_data.get("password")
        validate_password(password)
        return password

class AdditionalRegistrationForm(forms.Form):
    first_name = forms.CharField(label='first_name', max_length=100)
    last_name = forms.CharField(label='last_name', max_length=100)
    country = forms.CharField(label='country', max_length=100)
    company_name = forms.CharField(label='company_name', max_length=100, required=False)

class SearchForm(forms.Form):
    page = forms.IntegerField(label='page', required=False)
    min_price = forms.IntegerField(label='min_price', required=False)
    max_price = forms.IntegerField(label='max_price', required=False)
    category = forms.CharField(label='category', required=False)
    country = forms.CharField(label='country', required=False)

