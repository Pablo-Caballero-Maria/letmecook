from django.apps import AppConfig

class RecipesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recipes'
    
    def ready(self):
        import os
        from django.conf import settings
        # drop database
        from mongoengine.connection import get_connection
        connection = get_connection()
        connection.drop_database('letmecook')

        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'recipe_photos'), exist_ok=True)
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'ingredient_photos'), exist_ok=True)
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'profile_pictures'), exist_ok=True)

        from auth_app.models import User

        demo_user = User(
            username="pablito", 
            password_hash="1234",
            profile_picture="/media/default.jpg"
        )
        demo_user.save()

        # Seed default ingredients if none exist
        from .models import GlobalIngredient, Recipe, Comment
        if not GlobalIngredient.objects.first():
            defaults = [
                {
                    "name": "Tomato",
                    "calories": 18,
                    "fat": 0.2,
                    "carbohydrates": 3.9,
                    "protein": 0.9,
                    "allergens": [],
                    "photo": "/media/tomato.png"
                },
                {
                    "name": "Chicken Breast",
                    "calories": 165,
                    "fat": 3.6,
                    "carbohydrates": 0,
                    "protein": 31,
                    "allergens": [],
                    "photo": "/media/breast.jpg"
                },
                {
                    "name": "Olive Oil",
                    "calories": 884,
                    "fat": 100,
                    "carbohydrates": 0,
                    "protein": 0,
                    "allergens": [],
                    "photo": "/media/oil.jpg"
                },
                {
                    "name": "Broccoli",
                    "calories": 34,
                    "fat": 0.4,
                    "carbohydrates": 6.6,
                    "protein": 2.8,
                    "allergens": [],
                    "photo": "/media/broccoli.jpg"
                }
            ]
            for ing in defaults:
                GlobalIngredient(**ing).save()

        if not Recipe.objects.first():
            mock_recipes = [
                {
                    "title": "Classic Spaghetti Bolognese",
                    "description": "A hearty Italian meat sauce served over spaghetti.",
                    "tags": ["italian", "pasta", "dinner"],
                    "likes": 24,
                    "dislikes": 2,
                    "duration": 45,
                    "photo": "/media/spaghetti.jpg",
                    "owner": demo_user,
                    "ingredients": [
                        {
                            "name": "Tomato", 
                            "calories": 18,
                            "fat": 0.2,
                            "carbohydrates": 3.9,
                            "protein": 0.9,
                            "allergens": [],
                            "quantity": 5,
                            "photo": "/media/tomato.png"
                        },
                        {
                            "name": "Olive Oil", 
                            "calories": 884,
                            "fat": 100,
                            "carbohydrates": 0,
                            "protein": 0,
                            "allergens": [],
                            "quantity": 2,
                            "photo": "/media/oil.jpg"
                        }
                    ],
                    "comments": [
                    Comment(text="Great recipe!", author=demo_user),
                    Comment(text="My family loved this.", author=demo_user)
                    ]
                },
                {
                    "title": "Vegetable Stir Fry",
                    "description": "Quick and healthy vegetable stir fry with soy sauce.",
                    "tags": ["vegetarian", "quick", "dinner"],
                    "likes": 18,
                    "dislikes": 1,
                    "duration": 20,
                    "photo": "/media/stirfry.png",
                    "owner": demo_user,
                    "ingredients": [
                        {
                            "name": "Broccoli", 
                            "calories": 34,
                            "fat": 0.4,
                            "carbohydrates": 6.6,
                            "protein": 2.8,
                            "allergens": [],
                            "quantity": 2,
                            "photo": "/media/broccoli.jpg"
                        },
                        {
                            "name": "Olive Oil", 
                            "calories": 884,
                            "fat": 100,
                            "carbohydrates": 0,
                            "protein": 0,
                            "allergens": [],
                            "quantity": 1,
                            "photo": "/media/oil.jpg"
                        }
                    ],
                    "comments": [
                    Comment(text="So quick and easy!", author=demo_user),
                    Comment(text="Added tofu for protein.", author=demo_user)
                    ]                
                    },
                    {
                    "title": "Grilled Chicken Salad",
                    "description": "A light and healthy salad with grilled chicken breast and fresh tomatoes.",
                    "tags": ["healthy", "lunch", "protein"],
                    "likes": 15,
                    "dislikes": 2,
                    "duration": 25,
                    "photo": "/media/spaghetti.jpg",  # Reusing existing photo, ideally replace with salad
                    "owner": demo_user,
                    "ingredients": [
                        {
                            "name": "Chicken Breast", 
                            "calories": 165,
                            "fat": 3.6,
                            "carbohydrates": 0,
                            "protein": 31,
                            "allergens": [],
                            "quantity": 1,
                            "photo": "/media/breast.jpg"
                        },
                        {
                            "name": "Tomato", 
                            "calories": 18,
                            "fat": 0.2,
                            "carbohydrates": 3.9,
                            "protein": 0.9,
                            "allergens": [],
                            "quantity": 2,
                            "photo": "/media/tomato.png"
                        },
                        {
                            "name": "Olive Oil", 
                            "calories": 884,
                            "fat": 100,
                            "carbohydrates": 0,
                            "protein": 0,
                            "allergens": [],
                            "quantity": 1,
                            "photo": "/media/oil.jpg"
                        }
                    ],
                    "comments": [
                        Comment(text="Perfect summer meal!", author=demo_user),
                        Comment(text="I added cucumbers too.", author=demo_user)
                    ]
                },
                # New recipe 2: Chicken and Broccoli Bake
                {
                    "title": "Chicken and Broccoli Bake",
                    "description": "A comforting casserole with tender chicken and nutritious broccoli.",
                    "tags": ["comfort food", "dinner", "family"],
                    "likes": 32,
                    "dislikes": 3,
                    "duration": 50,
                    "photo": "/media/stirfry.png",  # Reusing existing photo, ideally replace with bake
                    "owner": demo_user,
                    "ingredients": [
                        {
                            "name": "Chicken Breast", 
                            "calories": 165,
                            "fat": 3.6,
                            "carbohydrates": 0,
                            "protein": 31,
                            "allergens": [],
                            "quantity": 2,
                            "photo": "/media/breast.jpg"
                        },
                        {
                            "name": "Broccoli", 
                            "calories": 34,
                            "fat": 0.4,
                            "carbohydrates": 6.6,
                            "protein": 2.8,
                            "allergens": [],
                            "quantity": 3,
                            "photo": "/media/broccoli.jpg"
                        },
                        {
                            "name": "Olive Oil", 
                            "calories": 884,
                            "fat": 100,
                            "carbohydrates": 0,
                            "protein": 0,
                            "allergens": [],
                            "quantity": 1,
                            "photo": "/media/oil.jpg"
                        }
                    ],
                    "comments": [
                        Comment(text="My kids ate all their broccoli!", author=demo_user),
                        Comment(text="Great weeknight dinner option.", author=demo_user)
                    ]
                },
                # New recipe 3: Bruschetta
                {
                    "title": "Classic Bruschetta",
                    "description": "Traditional Italian appetizer with fresh tomatoes and olive oil on toasted bread.",
                    "tags": ["italian", "appetizer", "vegetarian"],
                    "likes": 27,
                    "dislikes": 1,
                    "duration": 15,
                    "photo": "/media/spaghetti.jpg",  # Reusing existing photo, ideally replace with bruschetta
                    "owner": demo_user,
                    "ingredients": [
                        {
                            "name": "Tomato", 
                            "calories": 18,
                            "fat": 0.2,
                            "carbohydrates": 3.9,
                            "protein": 0.9,
                            "allergens": [],
                            "quantity": 4,
                            "photo": "/media/tomato.png"
                        },
                        {
                            "name": "Olive Oil", 
                            "calories": 884,
                            "fat": 100,
                            "carbohydrates": 0,
                            "protein": 0,
                            "allergens": [],
                            "quantity": 2,
                            "photo": "/media/oil.jpg"
                        }
                    ],
                    "comments": [
                        Comment(text="Perfect for summer gatherings!", author=demo_user),
                        Comment(text="I added some garlic, delicious!", author=demo_user)
                    ]
                },
                # New recipe 4: Sheet Pan Chicken and Vegetables
                {
                    "title": "Sheet Pan Chicken and Vegetables",
                    "description": "Easy one-pan meal with roasted chicken breast and seasonal vegetables.",
                    "tags": ["easy", "one-pan", "dinner"],
                    "likes": 41,
                    "dislikes": 2,
                    "duration": 45,
                    "photo": "/media/stirfry.png",  # Reusing existing photo, ideally replace
                    "owner": demo_user,
                    "ingredients": [
                        {
                            "name": "Chicken Breast", 
                            "calories": 165,
                            "fat": 3.6,
                            "carbohydrates": 0,
                            "protein": 31,
                            "allergens": [],
                            "quantity": 2,
                            "photo": "/media/breast.jpg"
                        },
                        {
                            "name": "Broccoli", 
                            "calories": 34,
                            "fat": 0.4,
                            "carbohydrates": 6.6,
                            "protein": 2.8,
                            "allergens": [],
                            "quantity": 2,
                            "photo": "/media/broccoli.jpg"
                        },
                        {
                            "name": "Tomato", 
                            "calories": 18,
                            "fat": 0.2,
                            "carbohydrates": 3.9,
                            "protein": 0.9,
                            "allergens": [],
                            "quantity": 3,
                            "photo": "/media/tomato.png"
                        },
                        {
                            "name": "Olive Oil", 
                            "calories": 884,
                            "fat": 100,
                            "carbohydrates": 0,
                            "protein": 0,
                            "allergens": [],
                            "quantity": 2,
                            "photo": "/media/oil.jpg"
                        }
                    ],
                    "comments": [
                        Comment(text="Minimal cleanup is a huge plus!", author=demo_user),
                        Comment(text="This has become a weekly staple.", author=demo_user)
                    ]
                }
            ]
            
            from .models import Ingredient
            for recipe_data in mock_recipes:
                ingredients_data = recipe_data.pop("ingredients")
                recipe = Recipe(**recipe_data)
                
                recipe_ingredients = []
                for ing_data in ingredients_data:
                    ingredient = Ingredient(**ing_data)
                    recipe_ingredients.append(ingredient)
                
                recipe.ingredients = recipe_ingredients
                recipe.save()
