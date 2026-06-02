from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('chat/', views.chat_page, name='chat'),
]