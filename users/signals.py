from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import CartItems,Cart
from django.http import HttpRequest
from django.contrib.sessions.models import Session



@receiver(user_logged_in)
def initalize_cart_session(sender,request:HttpRequest,user,**kwargs):
    # cart_items = CartItems.objects.select_related('cart__user','product_variant').filter(cart__user=user).values('product_variant__id','qty','cart__products_count')
    # cart_item_count = cart_items[0]['cart__products_count'] if cart_items and cart_items[0] else 0

    # cart = dict()
    # for item in cart_items:
    #     item_id = int(item.get('product_variant__id',None))
    #     qty = int(item.get('qty',None))

    #     if item_id:
    #         cart[item_id] = qty


    cart_item_count = CartItems.objects.select_related('cart__user').filter(cart__user=user).count()

    
    request.session['cart'] = dict()
    request.session['cart_item_count'] = cart_item_count
    

