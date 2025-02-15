from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.forms import ModelForm, Select, Textarea, TextInput

from .models import Snippet, User
import re



class AdminUserCreate(ModelForm):
    password1 = forms.CharField(
        min_length=8,
        max_length=20,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
            }),
    )
    password2 = forms.CharField(
        min_length=8,
        max_length=20,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
            })
    )

    class Meta:
        model = User
        fields = ("email", )
        widgets = {
            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control tall-form-field',
                })
        }

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        new_email = User.objects.filter(email=email)
        if new_email.count():
            raise forms.ValidationError(
                "Cant create user. Email is probably repeated.")
        return email

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        pwd = password1.lower()
        reg = "^(?=.*[a-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,20}$"
        # compiling regex
        pat = re.compile(reg)
        # searching regex
        mat = re.search(pat, pwd)
        if not mat:
            raise forms.ValidationError("The password does not comply with the requested format.")
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 != password2:
            raise forms.ValidationError("The Confirm Password field does not match the Password field.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data.get("password1"))
        if commit:
            user.save()
        return user


class UserAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="",
        widget=forms.EmailInput(
            attrs={"class": "form-control tall-form-field mb-4"}
        ),
    )
    password = forms.CharField(
        label="",
        widget=forms.PasswordInput(
            attrs={"class": "form-control tall-form-field mb-4"}
        ),
    )

    class Meta:
        model = User
        fields = ("username", "password")


class UserRegisterForm(forms.ModelForm):
    email = forms.EmailField(
        label="",
        widget=forms.TextInput(),
    )

    password1 = forms.CharField(
        label="",
        widget=forms.PasswordInput(),
    )
    password2 = forms.CharField(
        label="",
        widget=forms.PasswordInput(),
    )

    class Meta:
        model = User
        fields = ("email", )

    def email_clean(self):
        email = self.cleaned_data["email"].lower()
        new_email = User.objects.filter(email=email)
        if new_email.count():
            raise ValidationError("Email already exist")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user



class SnippetForm(ModelForm):
    class Meta:
        model = Snippet
        fields = ["name", "description", "language", "public", "snippet"]
        labels = {
            "name": "Nombre",
            "description": "Descripción",
            "language": "Lenguaje",
            "public": "Público",
            "snippet": "Snippet",
        }
        widgets = {
            "name": TextInput(
                attrs={"class": "form-control", "placeholder": "Nombre del snippet"}
            ),
            "description": TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Descripción del snippet",
                }
            ),
            "language": Select(attrs={"class": "form-control"}),
            "snippet": Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "/* Código del snippet */",
                }
            ),
        }
