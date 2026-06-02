from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_page, name='login'),
    path('chat/', views.chat_page, name='chat'),
]