from django.shortcuts import render, redirect
from mongoengine.errors import NotUniqueError, DoesNotExist

def home(request):
    if request.method == "POST":
        name = request.POST.get("name")
        message = request.POST.get("message")
        # TODO: send this message somewhere
        return redirect("home")
    return render(request, 'home.html')