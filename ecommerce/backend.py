from django.core.validators import validate_email
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class UserNameOREmailBackend(BaseBackend):
    def authenticate(self, request, username = None ,password = None):
        try:
            validate_email(username)
            kwarg = {'email':username}
        except:
            kwarg = {'username':username}

        try:
            user = User.objects.get(**kwarg)
        except User.DoesNotExist:
            return None
        
        if user.check_password(password):
            return user
        
        return None
    
    def get_user(self, user_id):
        try:
            user = User.objects.get(pk=user_id)
            return user
        except User.DoesNotExist:
            return None

        

