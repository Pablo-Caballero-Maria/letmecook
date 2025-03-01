import os

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from mongoengine.errors import DoesNotExist, NotUniqueError
from mongoengine.queryset.visitor import Q

from recipes.models import Recipe

from .models import Message, User


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        profile_pic = request.FILES.get("profile_picture")

        if not (username and password and profile_pic):
            return render(
                request, "register.html", {"error": "All fields are required."}
            )
        try:
            user = User(username=username)
            user.set_password(password)

            upload_dir = os.path.join(settings.MEDIA_ROOT, "profile_pictures")
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
            return render(
                request, "register.html", {"error": "Username already exists."}
            )
    return render(request, "register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                request.session["user_id"] = str(user.id)
                return redirect("home")
            else:
                return render(request, "login.html", {"error": "Invalid credentials."})
        except DoesNotExist:
            return render(request, "login.html", {"error": "Invalid credentials."})
    return render(request, "login.html")


def logout_view(request):
    request.session.flush()
    return redirect("home")


def user_profile_view(request, username):
    try:
        # Get the viewed user
        profile_user = User.objects.get(username=username)

        # Get the current user if logged in
        current_user = None
        user_id = request.session.get("user_id")
        if user_id:
            current_user = User.objects.get(id=user_id)

        # Get recipes created by this user
        user_recipes = Recipe.objects(owner=profile_user)[
            :5
        ]  # Limit to 5 recent recipes

        # Check if the current user follows this user
        is_following = False
        if current_user:
            is_following = current_user in profile_user.followers

        context = {
            "profile_user": profile_user,
            "user_recipes": user_recipes,
            "is_following": is_following,
            "followers_count": len(profile_user.followers),
            "following_count": len(profile_user.following),
        }

        return render(request, "user_profile.html", context)
    except User.DoesNotExist:
        return redirect("home")  # Redirect to home if user doesn't exist


def follow_user_view(request, username):
    if request.method == "POST":
        user_id = request.session.get("user_id")
        if not user_id:
            return JsonResponse({"success": False, "error": "login_required"})

        try:
            current_user = User.objects.get(id=user_id)
            target_user = User.objects.get(username=username)

            # Don't allow following yourself
            if current_user.id == target_user.id:
                return JsonResponse({"success": False, "error": "cannot_follow_self"})

            # Toggle follow status
            if current_user in target_user.followers:
                # Unfollow
                target_user.followers.remove(current_user)
                current_user.following.remove(target_user)
                followed = False
            else:
                # Follow
                target_user.followers.append(current_user)
                current_user.following.append(target_user)
                followed = True

            target_user.save()
            current_user.save()

            # Return JSON response
            return JsonResponse(
                {
                    "success": True,
                    "followed": followed,
                    "followers_count": len(target_user.followers),
                }
            )
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request"})


def friends_view(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    try:
        user = User.objects.get(id=user_id)
        following = user.following
        followers = user.followers

        return render(
            request,
            "friends.html",
            {"following": following, "followers": followers, "current_user": user},
        )
    except User.DoesNotExist:
        return redirect("login")


def chat_view(request, username):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    try:
        current_user = User.objects.get(id=user_id)
        other_user = User.objects.get(username=username)

        # Fetch messages between the two users
        # Messages where current_user is sender and other_user is recipient OR
        # Messages where other_user is sender and current_user is recipient
        messages = Message.objects(
            (
                (Q(sender=current_user) & Q(recipient=other_user))
                | (Q(sender=other_user) & Q(recipient=current_user))
            )
        ).order_by("timestamp")

        # Format messages for template
        formatted_messages = []
        for message in messages:
            formatted_messages.append(
                {
                    "id": str(message.id),
                    "sender_id": str(message.sender.id),
                    "sender_username": message.sender.username,
                    "sender_profile_picture": message.sender.profile_picture,
                    "text": message.text,
                    "timestamp": message.timestamp,
                }
            )

        return render(
            request,
            "chat.html",
            {
                "current_user": current_user,
                "current_user_id_str": str(current_user.id),
                "other_user": other_user,
                "messages": formatted_messages,
            },
        )
    except User.DoesNotExist:
        return redirect("login")


def send_message_view(request, username):
    user_id = request.session.get("user_id")
    if not user_id:
        return JsonResponse({"success": False, "error": "login_required"})

    if request.method == "POST":
        try:
            sender = User.objects.get(id=user_id)
            recipient = User.objects.get(username=username)
            message_text = request.POST.get("message", "").strip()

            if not message_text:
                return JsonResponse(
                    {"success": False, "error": "Message cannot be empty"}
                )

            # save message to database
            timestamp = timezone.now()
            message = Message(
                sender=sender,
                recipient=recipient,
                text=message_text,
                timestamp=timestamp,
            )
            message.save()

            message_dict = {
                "id": str(message.id),
                "sender_id": str(sender.id),
                "sender_username": sender.username,
                "sender_profile_picture": sender.profile_picture,
                "text": message_text,
                "timestamp": timestamp.strftime("%b %d, %I:%M %p"),
            }

            return JsonResponse({"success": True, "message": message_dict})
        except User.DoesNotExist:
            return JsonResponse({"success": False, "error": "User not found"})

    return JsonResponse({"success": False, "error": "Invalid request method"})
