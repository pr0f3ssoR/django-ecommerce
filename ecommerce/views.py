
from django.http import HttpRequest,HttpResponse


def checkout_success(request:HttpRequest):
    return HttpResponse('Successs')