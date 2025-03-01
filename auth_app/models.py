from mongoengine import (BooleanField, DateTimeField, Document, ListField,
                         ReferenceField, StringField)
from werkzeug.security import check_password_hash, generate_password_hash


class User(Document):
    username = StringField(required=True, unique=True)
    password_hash = StringField(required=True)
    saved_recipes = ListField(ReferenceField("Recipe"))
    profile_picture = StringField(
        default="/media/default_profile.png"
    )  # Default profile picture
    followers = ListField(ReferenceField("self", reverse_delete_rule=4), default=[])
    following = ListField(ReferenceField("self", reverse_delete_rule=4), default=[])

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Message(Document):
    sender = ReferenceField(User, required=True)
    recipient = ReferenceField(User, required=True)
    text = StringField(required=True)
    timestamp = DateTimeField(required=True)
    is_read = BooleanField(default=False)
