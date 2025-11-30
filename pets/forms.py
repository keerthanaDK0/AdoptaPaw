from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Profile, Pet, Feedback, Message

# Custom Registration Form with Role Selection
# forms.py

ROLE_CHOICES = [
    ('user', 'User'),
    ('doctor', 'Doctor'),
    ('admin', 'Admin'),
]

class CustomUserRegisterForm(UserCreationForm):
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            role = self.cleaned_data['role']
            Profile.objects.create(user=user, role=role)
        return user


class CustomLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=ROLE_CHOICES)


# Form to handle the creation of a pet
class PetForm(forms.ModelForm):
    PET_TYPES = [
        ('Dog', 'Dog'),
        ('Cat', 'Cat'),
        ('Bird', 'Bird'),
        ('Other', 'Other'),
    ]

    name = forms.CharField(max_length=100, required=True)
    pet_type = forms.ChoiceField(choices=PET_TYPES, required=True)
    breed = forms.CharField(max_length=100, required=False)
    age = forms.IntegerField(min_value=0, required=True)
    owner = forms.ModelChoiceField(queryset=User.objects.all(), required=True)
    image = forms.ImageField(required=False)
    is_approved = forms.BooleanField(required=False, initial=False)

    class Meta:
        model = Pet
        fields = ['name', 'pet_type', 'breed', 'age', 'owner', 'image', 'is_approved']

    def save(self, commit=True):
        pet = super().save(commit=False)
        if commit:
            pet.save()
        return pet



class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'email', 'message']

# Chat Message Form
class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Type your message...'}),
        }


# Doctor Clearance Request Form
class DoctorClearanceRequestForm(forms.Form):
    reason = forms.CharField(
        label='Reason for Request',
        widget=forms.Textarea(attrs={
            'placeholder': 'Enter the reason for your request...',
            'rows': 4,
            'class': 'form-control'
        }),
        max_length=500,
        required=True
    )
    additional_info = forms.CharField(
        label='Additional Information (Optional)',
        widget=forms.Textarea(attrs={
            'placeholder': 'Enter any additional details or information...',
            'rows': 4,
            'class': 'form-control'
        }),
        max_length=1000,
        required=False
    )


# Add Doctor Form (for Admin use)
class AddDoctorForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Profile
        fields = ['username', 'email', 'password', 'phone', 'specialization']


# forms.py
from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(max_length=255, required=True)
    email = forms.EmailField(required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)        