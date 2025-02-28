from .models import User
from mongoengine.errors import DoesNotExist

def current_user(request):
    user = None
    user_id = request.session.get('user_id')
    if user_id:
        try:
            user = User.objects.get(id=user_id)
        except DoesNotExist:
            pass
    return {'current_user': user}