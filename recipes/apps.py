from django.apps import AppConfig

class RecipesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recipes'
    
    def ready(self):
        # Seed default ingredients if none exist
        from .models import GlobalIngredient, Recipe
        if not GlobalIngredient.objects.first():
            defaults = [
                {
                    "name": "Tomato",
                    "calories": 18,
                    "fat": 0.2,
                    "carbohydrates": 3.9,
                    "protein": 0.9,
                    "allergens": [],
                    "tags": ["vegetable", "fruit"],
                },
                {
                    "name": "Chicken Breast",
                    "calories": 165,
                    "fat": 3.6,
                    "carbohydrates": 0,
                    "protein": 31,
                    "allergens": [],
                    "tags": ["meat", "protein"],
                },
                {
                    "name": "Olive Oil",
                    "calories": 884,
                    "fat": 100,
                    "carbohydrates": 0,
                    "protein": 0,
                    "allergens": [],
                    "tags": ["oil", "fat"],
                },
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
                    "ingredients": [
                        {
                            "name": "Tomato", 
                            "calories": 18,
                            "fat": 0.2,
                            "carbohydrates": 3.9,
                            "protein": 0.9,
                            "allergens": [],
                            "tags": ["vegetable", "fruit"],
                            "quantity": 5
                        },
                        {
                            "name": "Olive Oil", 
                            "calories": 884,
                            "fat": 100,
                            "carbohydrates": 0,
                            "protein": 0,
                            "allergens": [],
                            "tags": ["oil", "fat"],
                            "quantity": 2
                        },
                        {
                            "name": "Ground Beef", 
                            "calories": 250,
                            "fat": 15,
                            "carbohydrates": 0,
                            "protein": 26,
                            "allergens": [],
                            "tags": ["meat", "protein"],
                            "quantity": 2
                        }
                    ],
                    "comments": ["Great recipe!", "My family loved this."]
                },
                {
                    "title": "Vegetable Stir Fry",
                    "description": "Quick and healthy vegetable stir fry with soy sauce.",
                    "tags": ["vegetarian", "quick", "dinner"],
                    "likes": 18,
                    "dislikes": 1,
                    "duration": 20,
                    "ingredients": [
                        {
                            "name": "Broccoli", 
                            "calories": 34,
                            "fat": 0.4,
                            "carbohydrates": 6.6,
                            "protein": 2.8,
                            "allergens": [],
                            "tags": ["vegetable", "green"],
                            "quantity": 2
                        },
                        {
                            "name": "Olive Oil", 
                            "calories": 884,
                            "fat": 100,
                            "carbohydrates": 0,
                            "protein": 0,
                            "allergens": [],
                            "tags": ["oil", "fat"],
                            "quantity": 1
                        }
                    ],
                    "comments": ["So quick and easy!", "Added tofu for protein."]
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
