from userProfile.models import BlackListedToken,UserProfile

def get_user_object(username):
    if username:
        print(username)
        user = UserProfile.objects.filter(username=username)
        print("get_user_object",user[0])
        return user[0]