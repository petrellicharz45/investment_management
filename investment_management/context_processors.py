# context_processors.py

from .models import UserProfile  # Import your UserProfile model

def user_profile_context(request):
    # If the user is authenticated, fetch the user_profile and add it to the context
    user_profile = None
    if request.user.is_authenticated:
        user_profile = UserProfile.objects.get(user=request.user)

    return {'user_profile': user_profile}
