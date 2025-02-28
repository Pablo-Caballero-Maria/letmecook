from mongoengine import Document, StringField, ListField, ReferenceField
from werkzeug.security import generate_password_hash, check_password_hash

class User(Document):
    username = StringField(required=True, unique=True)
    password_hash = StringField(required=True)
    saved_recipes = ListField(ReferenceField('Recipe'))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)