from django.db import models
from django.contrib.auth.models import User,AbstractUser
from products.models import ProductVariant
from django.contrib.sessions.models import Session
from django.core.exceptions import ValidationError

# Create your models here.

class CustomUser(AbstractUser):

    email = models.EmailField(unique=True)
    REQUIRED_FIELDS = ['email']



class Cart(models.Model):
    products_count = models.PositiveIntegerField(default=0)
    user = models.OneToOneField('CustomUser',on_delete=models.CASCADE,null=True,blank=True)
    session= models.OneToOneField(Session,on_delete=models.CASCADE,null=True,blank=True)

    def clean(self):
        if not self.user and not self.session:
            raise(ValidationError('Profile and Session cannot be null!'))
        return super().clean()

class CartItems(models.Model):
    cart = models.ForeignKey('Cart',on_delete=models.CASCADE,related_name='cart_items')
    product_variant = models.ForeignKey(ProductVariant,on_delete=models.CASCADE)
    qty = models.PositiveIntegerField(default=0)


    class Meta:
        unique_together = ('cart', 'product_variant')