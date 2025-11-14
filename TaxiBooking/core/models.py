from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    license_plate = models.CharField(max_length=20)
    vehicle_type = models.CharField(max_length=50) # e.g., "Sedan", "SUV"
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username

class Booking(models.Model):
    # Ride Status Options
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )

    rider = models.ForeignKey(User, related_name='rides_as_rider', on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, related_name='rides_as_driver', on_delete=models.SET_NULL, null=True, blank=True)
    
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ride from {self.pickup_location} to {self.dropoff_location} ({self.status})"