from django.urls import path

from . import views

urlpatterns = [
    path("profile", views.profile_view, name="profile"),
    path("profile/edit", views.profile_edit_view, name="profile_edit"),
    path("profile/delete", views.profile_delete_view, name="profile_delete"),
]
