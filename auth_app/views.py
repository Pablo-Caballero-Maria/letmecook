from django.shortcuts import render, redirect
from mongoengine.errors import NotUniqueError, DoesNotExist
from .models import User

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        if not (username and password):
            return render(request, "register.html", {"error": "All fields are required."})
        try:
            user = User(username=username)
            user.set_password(password)
            user.save()
            return redirect("login")
        except NotUniqueError:
            return render(request, "register.html", {"error": "Username already exists."})
    return render(request, "register.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                request.session['user_id'] = str(user.id)
                return redirect("home")
            else:
                return render(request, "login.html", {"error": "Invalid credentials."})
        except DoesNotExist:
            return render(request, "login.html", {"error": "Invalid credentials."})
    return render(request, "login.html")

def logout_view(request):
    request.session.flush()
    return redirect('home')