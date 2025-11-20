from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Booking, Driver

# --- RIDER VIEWS ---

@login_required(login_url='login')
def index(request):
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

    my_rides = Booking.objects.filter(rider=request.user).order_by('-created_at')
    
    context = {
        'my_rides': my_rides
    }
    return render(request, 'RiderDashboard.html', context)

@login_required(login_url='login')
def cancel_ride(request, ride_id):
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
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index') 
    else:
        form = UserCreationForm()
    
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirect drivers to their dashboard, riders to theirs
                if hasattr(user, 'driver'):
                    return redirect('driver_dashboard')
                return redirect('index') 
    else:
        form = AuthenticationForm()
        
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

# --- DRIVER VIEWS ---

def driver_register_view(request):
    if request.method == 'POST':
        # We use the same UserCreationForm for the username/password
        form = UserCreationForm(request.POST)
        
        # We also get the extra driver data directly from the POST request
        license_plate = request.POST.get('license_plate')
        vehicle_type = request.POST.get('vehicle_type')
        
        if form.is_valid() and license_plate and vehicle_type:
            # 1. Create the User
            user = form.save()
            
            # 2. Create the Driver profile linked to that User
            Driver.objects.create(
                user=user,
                license_plate=license_plate,
                vehicle_type=vehicle_type
            )
            
            # 3. Log them in and redirect to the Driver Dashboard
            login(request, user)
            return redirect('driver_dashboard')
    else:
        form = UserCreationForm()
    
    return render(request, 'DriverRegistrationForm.html', {'form': form})

@login_required(login_url='login')
def driver_dashboard(request):
    try:
        driver_profile = request.user.driver
    except Driver.DoesNotExist:
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