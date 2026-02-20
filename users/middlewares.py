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

        response = self.get_response(request)

        return response
    



class LoggingMiddleware:
    def __init__(self,get_response):
        self.get_response = get_response

    def __call__(self,request:HttpRequest):

        # pprint(request.session.items())
        # session_key = request.COOKIES.get('sessionid',None)
        # if session_key:
        #     print(session_key)
        #     session = Session.objects.values().get(session_key=session_key)

        #     pprint(session)



        # pprint(request.META.get('HTTP_COOKIE'))

        # print(request.session.session_key)


        # pprint(request.session.session_key)

        # print(request.session.get('cart'))
        # print(request.session.get('cart_item_count'))

        response = self.get_response(request)

        return response