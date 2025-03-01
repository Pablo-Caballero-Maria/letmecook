from django.urls import path

from . import views

urlpatterns = [
    path("register", views.register_view, name="register"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("user/<username>", views.user_profile_view, name="user_profile"),
    path("user/<username>/follow", views.follow_user_view, name="follow_user"),
    path("friends/", views.friends_view, name="friends"),
    path("chat/<str:username>/", views.chat_view, name="chat"),
    path("chat/<str:username>/send", views.send_message_view, name="send_message"),
]
