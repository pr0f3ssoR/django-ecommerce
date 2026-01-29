from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Verification(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    verified = models.BooleanField(default=False)
    token = models.IntegerField(editable=False)
    created_at = models.DateField(auto_now_add=True)
    expire_at = models.DateField(editable=False)


    def get_expire_time(self):
        import time

        expire_time = time.time() + 120

        return expire_time
    
    def get_token(self):
        import secrets

        token = secrets.token_hex(16)

        return token

    def save(self, *args,**kwargs):
        self.expire_at = self.get_expire_time()
        self.token = self.get_token()

        return super().save(*args,**kwargs)