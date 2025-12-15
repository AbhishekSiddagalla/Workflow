from django.contrib import admin
from django.urls import path, include

from backend.views import LoginView, LogoutView, RefreshTokenView

urlpatterns = [
    path("token/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", RefreshTokenView.as_view(), name="refresh-token"),

]