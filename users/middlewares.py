from django.http import HttpRequest
from .models import Cart,CartItems
from products.models import ProductVariant
from pprint import pprint
from django.db import transaction
from django.contrib.sessions.models import Session

class CartMiddleWare:
    def __init__(self,get_response):
        self.get_response = get_response

    def __call__(self,request:HttpRequest):

        session_key = request.session.session_key

        if not session_key:
            session_key = request.session.save()
            request.session['cart'] = dict()
            request.session['cart_item_count'] = 0

        elif request.user.is_authenticated:
            cart_item_count = CartItems.objects.select_related('cart__user').filter(cart__user=request.user).count()
            request.session['cart'] = dict()
            request.session['cart_item_count'] = cart_item_count

        response = self.get_response(request)

        return response
    



class LoggingMiddleware:
    def __init__(self,get_response):
        self.get_response = get_response

    def __call__(self,request:HttpRequest):


        response = self.get_response(request)

        return response