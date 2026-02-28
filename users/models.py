from django.db import models
from django.contrib.auth.models import User,AbstractUser,BaseUserManager
from products.models import ProductVariant
from django.contrib.sessions.models import Session
from django.core.exceptions import ValidationError
import uuid

# Create your models here.


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user"""
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        
        # Set default values for non-superuser
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        
        # Create the user
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        
        # Create cart for the user
        from .models import Cart  # Import here to avoid circular imports
        Cart.objects.create(user=user)
        
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if 'username' not in extra_fields:
            # Generate username from email or set a default
            extra_fields['username'] = email.split('@')[0]  # or use a UUID
            
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        # Create the superuser
        user = self.create_user(email, password, **extra_fields)
        
        return user

class CustomUser(AbstractUser):

    email = models.EmailField(unique=True)
    REQUIRED_FIELDS = ['email']

    objects = UserManager()


class Cart(models.Model):
    products_count = models.PositiveIntegerField(default=0)
    user = models.OneToOneField('CustomUser',on_delete=models.CASCADE,null=True,blank=True)
    session= models.OneToOneField(Session,on_delete=models.CASCADE,null=True,blank=True)

    def clean(self):
        if not self.user and not self.session:
            raise(ValidationError('Profile and Session cannot be null!'))
        return super().clean()
    
    def save(self, *args,**kwargs):
        product_count = CartItems.objects.filter(cart_id=self.pk).count()
        self.products_count = product_count
        return super().save(*args,**kwargs)

class CartItems(models.Model):
    cart = models.ForeignKey('Cart',on_delete=models.CASCADE,related_name='cart_items')
    product_variant = models.ForeignKey(ProductVariant,on_delete=models.CASCADE)
    qty = models.PositiveIntegerField(default=0)


    class Meta:
        unique_together = ('cart', 'product_variant')


class Order(models.Model):
    invoice = models.UUIDField(primary_key=True,default=uuid.uuid4)
    user = models.ForeignKey('CustomUser',on_delete=models.CASCADE,null=True,blank=True)
    tracking_id = models.CharField(max_length=500,null=True,blank=True)
    created = models.DateField(auto_now_add=True)


class OrderItems(models.Model):
    order = models.OneToOneField(Order,on_delete=models.CASCADE)
    item = models.ForeignKey(ProductVariant,on_delete=models.SET_NULL,null=True)
    qty = models.PositiveIntegerField(default=1)



class ShippingAddress(models.Model):
    order = models.OneToOneField(Order,on_delete=models.CASCADE)
    first_name = models.CharField(max_length=9999,null=True,blank=True)
    last_name = models.CharField(max_length=9999,null=True,blank=True)
    phone = models.PositiveBigIntegerField()
    city = models.CharField(max_length=999)
    address = models.TextField()