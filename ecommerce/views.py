
from django.http import HttpRequest,HttpResponse
from django.shortcuts import render

def order_success(request:HttpRequest):
    
    return render(request,'users/order_success.html')