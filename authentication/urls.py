from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # API endpoints for ZKP
    path('challenge/', views.zkp_challenge, name='zkp_challenge'),
    path('verify/', views.zkp_verify, name='zkp_verify'),
]