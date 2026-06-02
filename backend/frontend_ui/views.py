from django.shortcuts import render

def login_page(request):
    return render(request, "login.html")

def chat_page(request):
    return render(request, "chat.html")