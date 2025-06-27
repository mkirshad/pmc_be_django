# accounts/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import RegisterView, LoginView, ProfileView, ResetPasswordView, FindUserView, \
    ResetForgotPassword, ListInspectorsView, CreateInspectorUserView, generate_captcha

router = DefaultRouter()

# Registering views with the router
router.register(r'register', RegisterView, basename='register')
router.register(r'login', LoginView, basename='login')
router.register(r'profile', ProfileView, basename='profile')
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('reset-password2/', ResetPasswordView.as_view(), name='reset-password'),
    path('find-user/', FindUserView.as_view(), name='find-user'),
    path('reset-forgot-password/', ResetForgotPassword.as_view(), name='reset-forgot-password'),
    path('list-inspectors/', ListInspectorsView.as_view(), name='list-inspectors'),
    path('create-update-inpsector-user/', CreateInspectorUserView.as_view(), name='list-inspectors'),
    path('generate-captcha/', generate_captcha, name='generate-captcha'),

]
