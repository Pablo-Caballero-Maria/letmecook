from django.shortcuts import render, redirect
from mongoengine.errors import NotUniqueError, DoesNotExist
from .models import User
import os
from django.conf import settings

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        profile_pic = request.FILES.get("profile_picture")

        if not (username and password and profile_pic):
            return render(request, "register.html", {"error": "All fields are required."})
        try:
            user = User(username=username)
            user.set_password(password)

            upload_dir = os.path.join(settings.MEDIA_ROOT, 'profile_pictures')
            os.makedirs(upload_dir, exist_ok=True)
                
            # Save with unique filename
            filename = f"{username}_{profile_pic.name}"
            filepath = os.path.join(upload_dir, filename)
            
            with open(filepath, "wb+") as destination:
                for chunk in profile_pic.chunks():
                    destination.write(chunk)
            
            user.profile_picture = f"/media/profile_pictures/{filename}"

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