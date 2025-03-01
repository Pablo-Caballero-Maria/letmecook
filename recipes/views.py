import os

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, render
from mongoengine.errors import DoesNotExist

from auth_app.models import User

from .models import GlobalIngredient, Ingredient, Recipe


def my_recipes_view(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    # Add pagination
    page = int(request.GET.get("page", 1))
    per_page = 4  # Same as explore_recipes_view for consistency

    # Get all recipes for the user
    all_recipes = Recipe.objects(owner=user_id)
    available_ingredients = GlobalIngredient.objects.all()

    # Get unique tags from all recipes
    all_recipe_objects = Recipe.objects.all()
    available_tags = sorted(
        set(tag for recipe in all_recipe_objects for tag in recipe.tags if recipe.tags)
    )

    # Paginate the recipes
    total = all_recipes.count()
    recipes = all_recipes.skip((page - 1) * per_page).limit(per_page)

    return render(
        request,
        "my_recipes.html",
        {
            "recipes": recipes,
            "ingredients": available_ingredients,
            "tags": available_tags,
            "current_page": page,
            "total_pages": (total + per_page - 1) // per_page,
        },
    )


def create_recipe_view(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")
    try:
        user = User.objects.get(id=user_id)
    except Exception as e:
        print(f"Error fetching user: {e}")
        request.session.flush()
        return redirect("login")

    if request.method == "POST":
        print("POST data:", request.POST)
        print("FILES data:", request.FILES)

        title = request.POST.get("title")
        description = request.POST.get("description")
        tags = request.POST.getlist("tags")
        ingredients = request.POST.getlist("ingredients")
        quantities = request.POST.getlist("quantities")
        duration = request.POST.get("duration")
        photo = request.FILES.get("photo")

        recipe = Recipe(
            title=title,
            description=description,
            tags=tags,
            duration=int(duration) if duration else None,
            owner=user,
        )

        if photo:
            upload_dir = os.path.join(settings.MEDIA_ROOT, "recipe_photos")
            os.makedirs(upload_dir, exist_ok=True)

            # Generate unique filename
            filename = f"{user_id}_{photo.name}"
            filepath = os.path.join(upload_dir, filename)

            with open(filepath, "wb+") as destination:
                for chunk in photo.chunks():
                    destination.write(chunk)

            # Store the URL
            recipe.photo = f"/media/recipe_photos/{filename}"
        recipe.save()

        # Process ingredients with quantities and nutritional info
        if ingredients:
            recipe_ingredients = []
            for i, name in enumerate(ingredients):
                try:
                    global_ing = GlobalIngredient.objects.get(name=name)
                    quantity = int(quantities[i]) if i < len(quantities) else 1

                    ingredient = Ingredient(
                        name=name,
                        calories=global_ing.calories,
                        fat=global_ing.fat,
                        carbohydrates=global_ing.carbohydrates,
                        protein=global_ing.protein,
                        allergens=global_ing.allergens,
                        quantity=quantity,
                        photo=global_ing.photo,
                    )
                    recipe_ingredients.append(ingredient)
                except DoesNotExist:
                    pass

            recipe.ingredients = recipe_ingredients
            recipe.save()
        return redirect("my_recipes")

    return redirect("my_recipes")


def recipe_update_view(request, recipe_id):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")
    try:
        recipe = Recipe.objects.get(id=recipe_id, owner=user_id)
    except DoesNotExist:
        return redirect("my_recipes")

    from .models import GlobalIngredient, Ingredient

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        tags = request.POST.getlist("tags")  # Get all tags as list
        ingredients = request.POST.getlist("ingredients")  # Get all ingredients as list
        quantities = request.POST.getlist("quantities")  # Get all quantities as list
        likes = request.POST.get("likes")
        dislikes = request.POST.get("dislikes")
        duration = request.POST.get("duration")
        photo = request.FILES.get("photo")

        recipe.title = title
        recipe.description = description
        recipe.tags = tags
        recipe.likes = int(likes) if likes else recipe.likes
        recipe.dislikes = int(dislikes) if dislikes else recipe.dislikes
        recipe.duration = int(duration) if duration else recipe.duration

        if photo:
            photo_path = f"recipe_photos/{photo.name}"
            with open(f"static/{photo_path}", "wb+") as destination:
                for chunk in photo.chunks():
                    destination.write(chunk)
            recipe.photo = f"/static/{photo_path}"

        # Update ingredients with quantities and nutritional info
        if ingredients:
            recipe_ingredients = []
            for i, name in enumerate(ingredients):
                try:
                    global_ing = GlobalIngredient.objects.get(name=name)
                    quantity = int(quantities[i]) if i < len(quantities) else 1

                    ingredient = Ingredient(
                        name=name,
                        calories=global_ing.calories,
                        fat=global_ing.fat,
                        carbohydrates=global_ing.carbohydrates,
                        protein=global_ing.protein,
                        allergens=global_ing.allergens,
                        quantity=quantity,
                        photo=global_ing.photo,
                    )
                    recipe_ingredients.append(ingredient)
                except DoesNotExist:
                    pass

            recipe.ingredients = recipe_ingredients

        recipe.save()
        return redirect("my_recipes")

    return redirect("my_recipes")


def recipe_delete_view(request, recipe_id):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")
    try:
        recipe = Recipe.objects.get(id=recipe_id, owner=user_id)
    except DoesNotExist:
        return redirect("my_recipes")
    if request.method == "POST":
        recipe.delete()
        return redirect("my_recipes")
    return render(request, "recipe_delete.html", {"recipe": recipe})


def rate_recipe_view(request, recipe_id):
    if request.method == "POST":
        user_id = request.session.get("user_id")
        if not user_id:
            return redirect("login")

        rating = int(request.POST.get("rating", 0))
        if not (1 <= rating <= 5):
            return redirect(f"/recipe/{recipe_id}")

        # Update the recipe with the new rating
        recipe = Recipe.objects.get(id=recipe_id)

        # Add rating model/field implementation
        # ...

        return redirect(f"/recipe/{recipe_id}")
    return redirect("home")


def add_comment_view(request, recipe_id):
    if request.method == "POST":
        user_id = request.session.get("user_id")
        if not user_id:
            return JsonResponse({"success": False, "error": "login_required"})

        comment_text = request.POST.get("comment")
        if not comment_text:
            return JsonResponse({"success": False, "error": "empty_comment"})

        try:
            recipe = Recipe.objects.get(id=recipe_id)
            user = User.objects.get(id=user_id)

            # Create a new Comment object
            from .models import Comment

            comment = Comment(text=comment_text, author=user)

            # Add to comments list
            if not recipe.comments:
                recipe.comments = []
            recipe.comments.append(comment)
            recipe.save()

            return JsonResponse(
                {
                    "success": True,
                    "username": user.username,
                    "user_profile_picture": user.profile_picture,
                    "comment_text": comment_text,
                }
            )
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "invalid_request"})


def explore_recipes_view(request):
    user_id = request.session.get("user_id")
    page = int(request.GET.get("page", 1))
    per_page = 4

    if user_id:
        user = User.objects.get(id=user_id)
        all_recipes = Recipe.objects(owner__ne=user.id).order_by("-id")
    else:
        all_recipes = Recipe.objects.order_by("-id")

    # Calculate pagination
    total = all_recipes.count()
    recipes = all_recipes.skip((page - 1) * per_page).limit(per_page)

    return render(
        request,
        "explore_recipes.html",
        {
            "recipes": recipes,
            "current_page": page,
            "total_pages": (total + per_page - 1) // per_page,
        },
    )


def search_view(request):
    query = request.GET.get("q", "")
    user_id = request.session.get("user_id")

    if query:
        # Search in titles, descriptions, ingredient names, and tags
        recipes = Recipe.objects(owner__ne=user_id if user_id else None).filter(
            __raw__={
                "$or": [
                    {"title": {"$regex": query, "$options": "i"}},
                    {"description": {"$regex": query, "$options": "i"}},
                    {"tags": {"$regex": query, "$options": "i"}},
                    {"ingredients.name": {"$regex": query, "$options": "i"}},
                ]
            }
        )
    else:
        recipes = []

    return render(request, "search_results.html", {"recipes": recipes, "query": query})


def like_recipe_view(request, recipe_id):
    if request.method == "POST":
        user_id = request.session.get("user_id")
        if not user_id:
            return JsonResponse({"success": False, "error": "login_required"})

        try:
            user = User.objects.get(id=user_id)
            recipe = Recipe.objects.get(id=recipe_id)

            # Track if we removed a dislike
            dislike_removed = False

            # Check if user previously disliked this recipe
            if user in recipe.disliked_by:
                recipe.disliked_by.remove(user)
                recipe.dislikes = max(0, recipe.dislikes - 1)
                dislike_removed = True

            # Toggle like
            if user in recipe.liked_by:
                recipe.liked_by.remove(user)
                recipe.likes = max(0, recipe.likes - 1)
                liked = False
            else:
                recipe.liked_by.append(user)
                recipe.likes += 1
                liked = True

            recipe.save()

            # Return JSON response
            return JsonResponse(
                {
                    "success": True,
                    "likes": recipe.likes,
                    "dislikes": recipe.dislikes,
                    "liked": liked,
                    "dislike_removed": dislike_removed,
                }
            )
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request"})


def dislike_recipe_view(request, recipe_id):
    if request.method == "POST":
        user_id = request.session.get("user_id")
        if not user_id:
            return JsonResponse({"success": False, "error": "login_required"})

        try:
            user = User.objects.get(id=user_id)
            recipe = Recipe.objects.get(id=recipe_id)

            # Track if we removed a like
            like_removed = False

            # Check if user previously liked this recipe
            if user in recipe.liked_by:
                recipe.liked_by.remove(user)
                recipe.likes = max(0, recipe.likes - 1)
                like_removed = True

            # Toggle dislike
            if user in recipe.disliked_by:
                recipe.disliked_by.remove(user)
                recipe.dislikes = max(0, recipe.dislikes - 1)
                disliked = False
            else:
                recipe.disliked_by.append(user)
                recipe.dislikes += 1
                disliked = True

            recipe.save()

            # Return JSON response
            return JsonResponse(
                {
                    "success": True,
                    "likes": recipe.likes,
                    "dislikes": recipe.dislikes,
                    "disliked": disliked,
                    "like_removed": like_removed,
                }
            )
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request"})


def save_recipe_view(request, recipe_id):
    if request.method == "POST":
        user_id = request.session.get("user_id")
        if not user_id:
            return JsonResponse({"success": False, "error": "login_required"})

        try:
            user = User.objects.get(id=user_id)
            recipe = Recipe.objects.get(id=recipe_id)

            # Toggle saved status
            if recipe in user.saved_recipes:
                user.saved_recipes.remove(recipe)
                saved = False
            else:
                user.saved_recipes.append(recipe)
                saved = True

            user.save()

            # Return JSON response
            return JsonResponse({"success": True, "saved": saved})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request"})


def saved_recipes_view(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    # Add pagination
    page = int(request.GET.get("page", 1))
    per_page = 4  # Same as explore_recipes_view for consistency

    user = User.objects.get(id=user_id)

    # Get total count of saved recipes
    total = len(user.saved_recipes) if user.saved_recipes else 0

    # Paginate saved recipes - need to handle differently since it's a list property
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paged_recipes = user.saved_recipes[start_idx:end_idx] if user.saved_recipes else []

    return render(
        request,
        "saved_recipes.html",
        {
            "recipes": paged_recipes,
            "current_page": page,
            "total_pages": (total + per_page - 1) // per_page,
        },
    )


def get_all_tags(request):
    """API endpoint to get all available tags"""
    from .models import Recipe

    # Get unique tags used in recipes
    all_recipes = Recipe.objects.all()
    available_tags = sorted(
        set(tag for recipe in all_recipes for tag in recipe.tags if recipe.tags)
    )

    return JsonResponse({"tags": available_tags})


def api_recipes_view(request):
    """API endpoint for recipes with filtering and sorting"""
    user_id = request.session.get("user_id")
    current_user = None
    if user_id:
        current_user = User.objects.get(id=user_id)

    # Get query parameters
    query = request.GET.get("q", "")
    tags = request.GET.get("tags", "")
    sort_by = request.GET.get("sort", "newest")
    page = int(request.GET.get("page", 1))
    per_page = 4
    my_recipes = request.GET.get("my_recipes", "false").lower() == "true"
    saved_recipes = request.GET.get("saved_recipes", "false").lower() == "true"

    # Build the query
    filters = {}

    # Filter by ownership or saved recipes
    if my_recipes and user_id:
        filters["owner"] = user_id
    elif saved_recipes and user_id and current_user:
        # We'll handle saved recipes separately since it's a list property on User
        pass
    elif not my_recipes and not saved_recipes and user_id:
        filters["owner__ne"] = user_id

    # Add text search if query provided
    if query:
        filters["__raw__"] = {
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
                {"tags": {"$regex": query, "$options": "i"}},
                {"ingredients.name": {"$regex": query, "$options": "i"}},
            ]
        }

    # Add tag filtering if tags provided
    if tags:
        tag_list = tags.split(",")
        if tag_list:
            if "__raw__" not in filters:
                filters["__raw__"] = {}
            filters["__raw__"]["tags"] = {"$all": tag_list}

    # Get the base query
    if saved_recipes and current_user and hasattr(current_user, "saved_recipes"):
        # For saved recipes, we need to get the IDs first
        saved_ids = [str(recipe.id) for recipe in current_user.saved_recipes]
        recipes_query = Recipe.objects(id__in=saved_ids, **filters)
    else:
        # Normal query
        recipes_query = Recipe.objects(**filters)

    # Sort the results
    if sort_by == "likes":
        recipes_query = recipes_query.order_by("-likes")
    elif sort_by == "duration-asc":
        recipes_query = recipes_query.order_by("duration")
    elif sort_by == "duration-desc":
        recipes_query = recipes_query.order_by("-duration")
    else:  # newest by default
        recipes_query = recipes_query.order_by("-id")

    # Calculate pagination
    total = recipes_query.count()
    recipes = recipes_query.skip((page - 1) * per_page).limit(per_page)

    # Format response
    result = []
    for recipe in recipes:
        recipe_data = {
            "id": str(recipe.id),
            "title": recipe.title,
            "description": recipe.description,
            "tags": recipe.tags,
            "likes": recipe.likes,
            "dislikes": recipe.dislikes,
            "duration": recipe.duration,
            "owner_username": recipe.owner.username if recipe.owner else "Unknown",
            "owner_profile_picture": recipe.owner.profile_picture,
            "comments": [
                {
                    "text": comment.text,
                    "author_username": comment.author.username,
                    "author_profile_picture": comment.author.profile_picture,
                }
                for comment in recipe.comments
            ],
            "user_liked": False,
            "user_disliked": False,
            "user_saved": False,
            "photo": recipe.photo,  # Include photo URL
            "ingredients": [
                {
                    "name": ing.name,
                    "calories": ing.calories,
                    "fat": ing.fat,
                    "carbohydrates": ing.carbohydrates,
                    "protein": ing.protein,
                    "quantity": ing.quantity,
                    "photo": ing.photo,
                }
                for ing in recipe.ingredients
            ],
        }

        # Add user-specific data if logged in
        if current_user:
            recipe_data["user_liked"] = (
                current_user in recipe.liked_by
                if hasattr(recipe, "liked_by")
                else False
            )
            recipe_data["user_disliked"] = (
                current_user in recipe.disliked_by
                if hasattr(recipe, "disliked_by")
                else False
            )
            recipe_data["user_saved"] = (
                recipe in current_user.saved_recipes
                if hasattr(current_user, "saved_recipes")
                else False
            )

        result.append(recipe_data)

    return JsonResponse(
        {
            "recipes": result,
            "total": total,
            "current_page": page,
            "total_pages": (total + per_page - 1) // per_page,
        }
    )
