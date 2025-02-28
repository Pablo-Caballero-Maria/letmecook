from mongoengine import Document, EmbeddedDocument, StringField, ListField, FloatField, IntField
from mongoengine import EmbeddedDocumentField, ReferenceField
from auth_app.models import User

class Ingredient(EmbeddedDocument):
    name = StringField(required=True)
    calories = FloatField(required=True)
    fat = FloatField(required=True)
    carbohydrates = FloatField(required=True)
    protein = FloatField(required=True)
    allergens = ListField(StringField())
    tags = ListField(StringField())
    quantity = IntField(default=1)

class Recipe(Document):
    title = StringField(required=True)
    description = StringField()
    tags = ListField(StringField())
    likes = IntField(default=0) 
    dislikes = IntField(default=0)
    comments = ListField(StringField())
    ingredients = ListField(EmbeddedDocumentField(Ingredient))
    duration = IntField()  # in minutes
    owner = ReferenceField(User)
    liked_by = ListField(ReferenceField(User))
    disliked_by = ListField(ReferenceField(User))

    @property
    def total_calories(self):
        return sum(ing.calories * (ing.quantity or 1) for ing in self.ingredients) if self.ingredients else 0
    
    @property
    def total_fat(self):
        return sum(ing.fat * (ing.quantity or 1) for ing in self.ingredients) if self.ingredients else 0
    
    @property
    def total_carbohydrates(self):
        return sum(ing.carbohydrates * (ing.quantity or 1) for ing in self.ingredients) if self.ingredients else 0
    
    @property
    def total_protein(self):
        return sum(ing.protein * (ing.quantity or 1) for ing in self.ingredients) if self.ingredients else 0

class GlobalIngredient(Document):
    name = StringField(required=True, unique=True)
    calories = FloatField(required=True)
    fat = FloatField(required=True)
    carbohydrates = FloatField(required=True)
    protein = FloatField(required=True)
    allergens = ListField(StringField())
    tags = ListField(StringField())