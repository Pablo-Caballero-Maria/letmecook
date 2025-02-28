from django.shortcuts import render, redirect
from mongoengine.errors import DoesNotExist
from auth_app.models import User
from .models import Recipe, Ingredient, GlobalIngredient
from django.http import JsonResponse

def my_recipes_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect("login")
    recipes = Recipe.objects(owner=user_id)
    available_ingredients = GlobalIngredient.objects.all()
    available_tags = sorted({ tag for ing in available_ingredients for tag in ing.tags })
    return render(request, 'my_recipes.html', {
        'recipes': recipes,
        'ingredients': available_ingredients,
        'tags': available_tags
    })

def create_recipe_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect("login")
    try:
        user = User.objects.get(id=user_id)
    except Exception as e:
        print(f"Error fetching user: {e}")
        request.session.flush()
        return redirect("login")
        
    available_ingredients = GlobalIngredient.objects.all()
    available_tags = sorted({ tag for ing in available_ingredients for tag in ing.tags })

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        tags = request.POST.getlist("tags")
        ingredients = request.POST.getlist("ingredients")
        quantities = request.POST.getlist("quantities")
        duration = request.POST.get("duration")
        
        recipe = Recipe(
            title=title,
            description=description,
            tags=tags,
            duration=int(duration) if duration else None,
            owner=user,
        )
        
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
                        tags=global_ing.tags,
                        quantity=quantity
                    )
                    recipe_ingredients.append(ingredient)
                except DoesNotExist:
                    pass
            
            recipe.ingredients = recipe_ingredients
        
        recipe.save()
        return redirect("my_recipes")
    
    return redirect("my_recipes")

def recipe_update_view(request, recipe_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect("login")
    try:
        recipe = Recipe.objects.get(id=recipe_id, owner=user_id)
    except DoesNotExist:
        return redirect("my_recipes")
    
    from .models import GlobalIngredient, Ingredient
    available_ingredients = GlobalIngredient.objects.all()
    available_tags = sorted({ tag for ing in available_ingredients for tag in ing.tags })
    
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        tags = request.POST.getlist("tags")  # Get all tags as list
        ingredients = request.POST.getlist("ingredients")  # Get all ingredients as list
        quantities = request.POST.getlist("quantities")  # Get all quantities as list
        likes = request.POST.get("likes")
        dislikes = request.POST.get("dislikes")
        duration = request.POST.get("duration")
        
        recipe.title = title
        recipe.description = description
        recipe.tags = tags
        recipe.likes = int(likes) if likes else recipe.likes
        recipe.dislikes = int(dislikes) if dislikes else recipe.dislikes
        recipe.duration = int(duration) if duration else recipe.duration
        
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
                        tags=global_ing.tags,
                        quantity=quantity
                    )
                    recipe_ingredients.append(ingredient)
                except DoesNotExist:
                    pass
            
            recipe.ingredients = recipe_ingredients
        
        recipe.save()
        return redirect("my_recipes")
    
    return redirect("my_recipes")

def recipe_delete_view(request, recipe_id):
    user_id = request.session.get('user_id')
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
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect("login")
        
        rating = int(request.POST.get('rating', 0))
        if not (1 <= rating <= 5):
            return redirect(f'/recipe/{recipe_id}')
        
        # Update the recipe with the new rating
        recipe = Recipe.objects.get(id=recipe_id)
        
        # Add rating model/field implementation
        # ...
        
        return redirect(f'/recipe/{recipe_id}')
    return redirect("home")

def add_comment_view(request, recipe_id):
    if request.method == "POST":
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'success': False, 'error': 'login_required'})
        
        comment = request.POST.get('comment')
        if not comment:
            return JsonResponse({'success': False, 'error': 'empty_comment'})
        
        try:
            recipe = Recipe.objects.get(id=recipe_id)
            if not recipe.comments:
                recipe.comments = []
                
            user = User.objects.get(id=user_id)
            comment_text = f"{user.username}: {comment}"
            recipe.comments.append(comment_text)
            recipe.save()
            
            return JsonResponse({
                'success': True,
                'comment': comment_text
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'invalid_request'})

def explore_recipes_view(request):
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)
        
    # Get recipes from other users, newest first, limit to 20
    recipes = Recipe.objects(owner__ne=user.id).order_by('-id').limit(20)
    
    return render(request, 'explore_recipes.html', {
        'recipes': recipes
    })

def search_view(request):
    query = request.GET.get('q', '')
    user_id = request.session.get('user_id')
    
    if query:
        # Search in titles, descriptions, ingredient names, and tags
        recipes = Recipe.objects(
            owner__ne=user_id if user_id else None
        ).filter(
            __raw__={
                '$or': [
                    {'title': {'$regex': query, '$options': 'i'}},
                    {'description': {'$regex': query, '$options': 'i'}},
                    {'tags': {'$regex': query, '$options': 'i'}},
                    {'ingredients.name': {'$regex': query, '$options': 'i'}}
                ]
            }
        )
    else:
        recipes = []
    
    return render(request, 'search_results.html', {
        'recipes': recipes,
        'query': query
    })

def like_recipe_view(request, recipe_id):
    if request.method == "POST":
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'success': False, 'error': 'login_required'})
            
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
            return JsonResponse({
                'success': True,
                'likes': recipe.likes,
                'dislikes': recipe.dislikes,
                'liked': liked,
                'dislike_removed': dislike_removed
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def dislike_recipe_view(request, recipe_id):
    if request.method == "POST":
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'success': False, 'error': 'login_required'})
            
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
            return JsonResponse({
                'success': True,
                'likes': recipe.likes,
                'dislikes': recipe.dislikes,
                'disliked': disliked,
                'like_removed': like_removed
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def save_recipe_view(request, recipe_id):
    if request.method == "POST":
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'success': False, 'error': 'login_required'})
            
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
            return JsonResponse({
                'success': True,
                'saved': saved
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def saved_recipes_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect("login")
        
    user = User.objects.get(id=user_id)
    return render(request, 'saved_recipes.html', {
        'recipes': user.saved_recipes
    })