from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):

    first_name = forms.CharField(max_length=100)

    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['first_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)

        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

        return user



# Customer Profile Form
class ProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['first_name', 'email']

        labels = {
            'first_name': 'First Name',
            'email': 'Email Address',
        }

        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your first name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email address'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data['email']

        existing_user = User.objects.exclude(
            pk=self.instance.pk
        ).filter(email__iexact=email).exists()

        if existing_user:
            raise forms.ValidationError(
                'This email address is already registered.'
            )

        existing_username = User.objects.exclude(
            pk=self.instance.pk
        ).filter(username__iexact=email).exists()

        if existing_username:
            raise forms.ValidationError(
                'This email address is already used by another account.'
            )

        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']

        if commit:
            user.save()

        return user
