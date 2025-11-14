...
from django.contrib import admin
from django.urls import path, include  # 'include' is already here, good!
from core.views import register_view, login_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path("__reload__/", include("django_browser_reload.urls")),
    path("", register_view, name="register"),  # Registration page
    path("login/", login_view, name="login"),  # Login page
]