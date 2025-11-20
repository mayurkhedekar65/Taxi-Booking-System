from django.urls import path
from . import views 

urlpatterns = [
    # --- FIX: This was missing! ---
    # This defines the URL name 'index' that caused your error
    path("", views.index, name="index"),
    
    # Auth URLs
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
]