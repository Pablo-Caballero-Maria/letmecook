from django.shortcuts import redirect, render
from mongoengine.errors import DoesNotExist, NotUniqueError


def home(request):
    if request.method == "POST":
        name = request.POST.get("name")
        message = request.POST.get("message")
        # TODO: send this message somewhere
        return redirect("home")
    return render(request, "home.html")
