from django.urls import path
from . import views

app_name = 'account'

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.user_signup, name='signup'),
    path('activate_user/<uuid:token>/', views.activate_user, name='activate_user'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('withdrawal/', views.user_withdrawal, name='withdrawal'),

    path('email/', views.user_email, name='email'),
    path('password/', views.user_password, name='password'),

    path('profile', views.user_profile, name='profile'),
]
