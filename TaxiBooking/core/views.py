from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required(login_url='login') # Protect this page
def index(request):
    """
    This is the main view for our home page (Rider Dashboard).
    """
    # For now, we are just showing the page.
    # Later, we will add the logic here to:
    # 1. Handle the 'INSERT' when a user books a ride (POST request).
    # 2. Handle the 'SELECT' to show the user's ride history (GET request).
    
    context = {
        'test_message': "Hello from the view!"
    }
    return render(request, 'RiderDashboard.html', context)
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('login.html') # Go to home page after signup
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
                return redirect('RiderDashboard.html') # Go to home page
    else:
        form = AuthenticationForm()
        
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login') # Go to login page after logout