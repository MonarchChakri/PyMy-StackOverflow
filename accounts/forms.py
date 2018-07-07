from django import forms
from django.contrib.auth.models import User


class SignUpForm(forms.Form):
    first_name = forms.CharField(
        required=True,
        max_length=75,
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'placeholder': 'Enter first name'}),
    )

    last_name = forms.CharField(
        required=True,
        max_length=75,
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'placeholder': 'Enter last name'}),
    )

    username = forms.CharField(
        required=True,
        max_length=75,
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'placeholder': 'Enter user name'}),
    )

    password = forms.CharField(
        required=True,
        max_length=75,
        widget=forms.PasswordInput(attrs={'class': 'form-control',
                                          'placeholder': 'Enter password'}),
    )


class LoginForm(forms.Form):
    username = forms.CharField(
        required=True,
        max_length=75,
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'placeholder': 'Enter user name'}),
    )

    password = forms.CharField(
        required=True,
        max_length=75,
        widget=forms.PasswordInput(attrs={'class': 'form-control',
                                          'placeholder': 'Enter password'}),
    )


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']
