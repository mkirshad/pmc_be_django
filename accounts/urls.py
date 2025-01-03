# accounts/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import RegisterView, LoginView, ProfileView

router = DefaultRouter()

# Registering views with the router
router.register(r'register', RegisterView, basename='register')
router.register(r'login', LoginView, basename='login')
router.register(r'profile', ProfileView, basename='profile')
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
]
