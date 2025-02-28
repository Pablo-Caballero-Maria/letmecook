from django.shortcuts import render, redirect
from auth_app.models import User
from mongoengine.errors import DoesNotExist
import os
from django.conf import settings

def profile_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect("login")
    try:
        user = User.objects.get(id=user_id)
    except:
        return redirect("login")
    return render(request, 'profile.html', {'user': user})

def profile_edit_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect("login")
    try:
        user = User.objects.get(id=user_id)
    except Exception:
        return redirect("login")
    if request.method == "POST":
        new_username = request.POST.get("username")
        new_password = request.POST.get("password")
        profile_pic = request.FILES.get("profile_picture")

        if new_username:
            user.username = new_username
        if new_password:
            user.set_password(new_password)

        if profile_pic:
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'profile_pictures')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate unique filename
            filename = f"{user.id}_{profile_pic.name}"
            filepath = os.path.join(upload_dir, filename)
            
            with open(filepath, "wb+") as destination:
                for chunk in profile_pic.chunks():
                    destination.write(chunk)
            
            user.profile_picture = f"/media/profile_pictures/{filename}"

        user.save()
        return redirect("profile")
    return render(request, "profile_edit.html", {"user": user})

def profile_delete_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect("login")
    try:
        user = User.objects.get(id=user_id)
    except Exception:
        return redirect("login")
    if request.method == "POST":
        user.delete()
        request.session.flush()  # clear session data after deletion
        return redirect("home")
    return render(request, "profile_delete.html", {"user": user})