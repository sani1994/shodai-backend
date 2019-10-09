from userProfile.models import BlackListedToken,UserProfile

def get_user_object(username):
    if username:
        user = UserProfile.objects.filter(username=username)
        return user[0]