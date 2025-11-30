from django.db import models
from django.contrib.auth.models import User

# Profile model for role-based access
class Profile(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('doctor', 'Doctor'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, default=1)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='user')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='active')
    phone = models.CharField(max_length=15, blank=True, null=True)
    specialization = models.CharField(max_length=100, blank=True, null=True)

    def _str_(self):
        return self.user.username if self.user else "No user assigned"


# Pet model
class Pet(models.Model):
    PET_TYPES = [
        ('Dog', 'Dog'),
        ('Cat', 'Cat'),
        ('Bird', 'Bird'),
        ('Other', 'Other'),
    ]
    name = models.CharField(max_length=100)
    pet_type = models.CharField(max_length=100)
    breed = models.CharField(max_length=100, default='Unknown')
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=[
        ('Male', 'Male'), 
        ('Female', 'Female'), 
        ('Unknown', 'Unknown')
    ], default='Unknown')
    description = models.TextField(default='No description available.')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pets_owner', null=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pets_selling', null=True)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pets_buying', null=True)
    image = models.ImageField(upload_to='pet_images/', blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    is_adopted = models.BooleanField(default=False)

    def _str_(self):
        return self.name


# Message model
class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)
    content = models.TextField()

    def _str_(self):
        return f"{self.sender} to {self.receiver}: {self.message[:30]}"


# Feedback model
class Feedback(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True)
    message = models.TextField()

    def _str_(self):
        return f'Feedback from {self.name}'


# AdoptionRequest model
class AdoptionRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='adoption_requests')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='adoption_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.user.username} - {self.pet.name} ({self.status})"


# SellerRequest model
class SellerRequest(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=[
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected')
    ], default='Pending')

    def _str_(self):
        return f"{self.seller.username} - {self.pet.name} - {self.status}"


# BuyerRequest model
class BuyerRequest(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buyer_requests')
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ], default='Pending')

    def _str_(self):
        return f"{self.buyer.username} - {self.pet.name} - {self.status}"


# DoctorClearanceRequest model
class DoctorClearanceRequest(models.Model):
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requested_clearances')
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_clearances', null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected')
    ], default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.pet.name} - {self.requested_by.username} - {self.status}"


# Contact model
class Contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"Message from {self.name} - {self.email}"
    
from django.db import models

class Product(models.Model):
    STATUS_CHOICES = [
        ('in_stock', 'In Stock'),
        ('sold', 'Sold'),
    ]
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='products/')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='in_stock')
    discount_percent = models.PositiveIntegerField(null=True, blank=True)
    rating = models.PositiveIntegerField(default=5)
    reviews = models.PositiveIntegerField(default=0)

    def is_discounted(self):
        return self.discount_price and self.discount_price < self.price

    def __str__(self):
        return self.name