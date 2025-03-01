from django.urls import path

from . import views

urlpatterns = [
    path("my-recipes", views.my_recipes_view, name="my_recipes"),
    path("recipe/new", views.create_recipe_view, name="recipe_create"),
    path("recipe/update/<recipe_id>", views.recipe_update_view, name="recipe_update"),
    path("recipe/delete/<recipe_id>", views.recipe_delete_view, name="recipe_delete"),
    path("explore", views.explore_recipes_view, name="explore_recipes"),
    path("search", views.search_view, name="search"),
    path("recipe/<recipe_id>/rate", views.rate_recipe_view, name="rate_recipe"),
    path("recipe/<recipe_id>/comment", views.add_comment_view, name="add_comment"),
    path("recipe/<recipe_id>/like", views.like_recipe_view, name="like_recipe"),
    path(
        "recipe/<recipe_id>/dislike", views.dislike_recipe_view, name="dislike_recipe"
    ),
    path("recipe/<recipe_id>/save", views.save_recipe_view, name="save_recipe"),
    path("saved-recipes", views.saved_recipes_view, name="saved_recipes"),
    path("api/tags", views.get_all_tags, name="api_tags"),
    path("api/recipes", views.api_recipes_view, name="api_recipes"),
]
