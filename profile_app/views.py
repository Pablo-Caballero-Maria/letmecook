from django.shortcuts import render, redirect
from auth_app.models import User
from mongoengine.errors import DoesNotExist

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
        if new_username:
            user.username = new_username
        if new_password:
            user.set_password(new_password)
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