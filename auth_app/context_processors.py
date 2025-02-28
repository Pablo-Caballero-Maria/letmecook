from .models import User
from mongoengine.errors import DoesNotExist

def current_user(request):
    user = None
    user_id = request.session.get('user_id')
    
    context = {}
    
    # Get demo user for comment display
    try:
        demo_user = User.objects.get(username="pablito")
        context['demo_user'] = demo_user
    except DoesNotExist:
        pass
    
    # Get current logged-in user
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            context['current_user'] = user
        except DoesNotExist:
            pass
    else:
        context['current_user'] = None
    
    return context