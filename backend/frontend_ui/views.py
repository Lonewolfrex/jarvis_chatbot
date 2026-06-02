from django.shortcuts import render
from django.views.decorators.cache import never_cache


@never_cache
def login_page(request):
    response = render(request, "login.html")
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    return response


@never_cache
def chat_page(request):
    response = render(request, "chat.html")
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    return response

@never_cache
def register_page(request):
    return render(request,"register.html")