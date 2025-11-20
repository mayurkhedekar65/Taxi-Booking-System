from django.db import models
from django.contrib.auth.models import User

# --- DRIVER MODEL ---
class Driver(models.Model):
    # Enforce choices for consistency in the database
    VEHICLE_CHOICES = (
        ('Sedan', 'Sedan (4 Seater)'),
        ('SUV', 'SUV (6 Seater)'),
        ('Hatchback', 'Hatchback (Small)'),
        ('Bike', 'Bike (1 Seater)'),
    )
    
    # Relationship: One User can be One Driver
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver')
    
    # DBMS Constraint: License plates must be unique across the system
    license_plate = models.CharField(max_length=20, unique=True)
    
    vehicle_type = models.CharField(max_length=50, choices=VEHICLE_CHOICES)
    is_available = models.BooleanField(default=True)
    
    # Audit field: When did this driver join?
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.license_plate}"

    class Meta:
        # DBMS Metadata
        db_table = 'core_driver'
        verbose_name = 'Driver Profile'
        verbose_name_plural = 'Driver Profiles'


# --- BOOKING MODEL ---
class Booking(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('In_Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )

    # Foreign Keys with Indexing implicitly enabled by Django
    rider = models.ForeignKey(User, related_name='rides_as_rider', on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, related_name='rides_as_driver', on_delete=models.SET_NULL, null=True, blank=True)
    
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    
    # Indexing: We frequently query by status (e.g., "Find all Pending rides")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending', db_index=True)
    
    # Proper Data Type for Money: Decimal is more precise than Float
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_booking'
        ordering = ['-created_at'] # Default sorting: Newest first
        
        # ADVANCED DBMS: Composite Index
        # This makes the query "Find Pending rides sorted by creation time" extremely fast
        indexes = [
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f"Ride #{self.id} ({self.status})"