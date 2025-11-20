from django.urls import path
from . import views 

urlpatterns = [
    # Rider URLs
    path("", views.index, name="index"),
    path("cancel/<int:ride_id>/", views.cancel_ride, name="cancel_ride"),
    
    # Auth URLs
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    
    # Driver URLs
    path("driver/", views.driver_dashboard, name="driver_dashboard"),
    path("accept/<int:ride_id>/", views.accept_ride, name="accept_ride"),
    path("complete/<int:ride_id>/", views.complete_ride, name="complete_ride"),
]