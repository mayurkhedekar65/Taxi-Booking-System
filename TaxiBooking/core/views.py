from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Booking, Driver

# --- RIDER VIEWS ---

@login_required(login_url='login')
def index(request):
    """
    Rider Dashboard: Book a ride and see history.
    """
    # 1. Redirect Drivers: Drivers should not see this page.
    if hasattr(request.user, 'driver'):
        return redirect('driver_dashboard')

    # 2. Handle Booking (INSERT)
    if request.method == 'POST':
        pickup = request.POST.get('pickup_location')
        dropoff = request.POST.get('dropoff_location')
        
        if pickup and dropoff:
            Booking.objects.create(
                rider=request.user,
                pickup_location=pickup,
                dropoff_location=dropoff,
                status='Pending'
            )
            return redirect('index')

    # 3. Handle History (SELECT)
    my_rides = Booking.objects.filter(rider=request.user).order_by('-created_at')
    
    context = {
        'my_rides': my_rides
    }
    return render(request, 'RiderDashboard.html', context)

@login_required(login_url='login')
def cancel_ride(request, ride_id):
    """
    Rider: Cancel a pending ride (DELETE).
    """
    if request.method == 'POST':
        try:
            ride = Booking.objects.get(id=ride_id, rider=request.user)
            if ride.status == 'Pending':
                ride.delete()
        except Booking.DoesNotExist:
            pass
    return redirect('index')

# --- AUTH VIEWS ---

def register_view(request):
    """
    Standard User Registration (Rider).
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        # Capture the new fields from the form
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        if form.is_valid() and first_name and last_name:
            # Save user but don't commit to DB yet
            user = form.save(commit=False)
            # Add the extra fields
            user.first_name = first_name
            user.last_name = last_name
            # Now save to DB
            user.save()
            
            login(request, user)
            return redirect('index') 
    else:
        form = UserCreationForm()
    
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    """
    Login page for both Riders and Drivers.
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                
                # Intelligent Redirect:
                # If user is a driver, go to Driver Dashboard
                if hasattr(user, 'driver'):
                    return redirect('driver_dashboard')
                
                # Otherwise, go to Rider Dashboard
                return redirect('index') 
    else:
        form = AuthenticationForm()
        
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

# --- DRIVER VIEWS ---

def driver_register_view(request):
    """
    Special Registration for Drivers (User + Driver Profile).
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        # Capture Name
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        # Capture Vehicle Details
        license_plate = request.POST.get('license_plate')
        vehicle_type = request.POST.get('vehicle_type')
        
        if form.is_valid() and license_plate and vehicle_type and first_name and last_name:
            # 1. Create the User with Name
            user = form.save(commit=False)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            
            # 2. Create the Driver profile linked to that User
            Driver.objects.create(
                user=user,
                license_plate=license_plate,
                vehicle_type=vehicle_type
            )
            
            login(request, user)
            return redirect('driver_dashboard')
    else:
        form = UserCreationForm()
    
    # Renders the correct template
    return render(request, 'DriverRegistrationForm.html', {'form': form})

@login_required(login_url='login')
def driver_dashboard(request):
    """
    Driver Dashboard: See available jobs and active rides.
    """
    # Check if user is a driver
    try:
        driver_profile = request.user.driver
    except Driver.DoesNotExist:
        # If not a driver, send them back to rider dashboard
        return redirect('index')

    available_rides = Booking.objects.filter(status='Pending', driver=None).order_by('-created_at')
    my_accepted_rides = Booking.objects.filter(driver=driver_profile, status='Accepted').order_by('-updated_at')

    context = {
        'available_rides': available_rides,
        'my_accepted_rides': my_accepted_rides
    }
    return render(request, 'DriverDashboard.html', context)

@login_required(login_url='login')
def accept_ride(request, ride_id):
    """
    Driver: Accept a pending ride (UPDATE).
    """
    if request.method == 'POST':
        try:
            driver_profile = request.user.driver
            ride = Booking.objects.get(id=ride_id)
            
            if ride.status == 'Pending':
                ride.driver = driver_profile
                ride.status = 'Accepted'
                ride.save()
                
        except (Driver.DoesNotExist, Booking.DoesNotExist):
            pass
            
    return redirect('driver_dashboard')

@login_required(login_url='login')
def complete_ride(request, ride_id):
    """
    Driver: Complete an active ride (UPDATE).
    """
    if request.method == 'POST':
        try:
            driver_profile = request.user.driver
            ride = Booking.objects.get(id=ride_id)
            
            if ride.driver == driver_profile and ride.status == 'Accepted':
                ride.status = 'Completed'
                ride.save()
                
        except (Driver.DoesNotExist, Booking.DoesNotExist):
            pass
            
    return redirect('driver_dashboard')