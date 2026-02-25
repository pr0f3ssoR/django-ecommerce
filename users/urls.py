from .views import register,cart_view,add_to_cart,delete_from_cart,check_out_view
from django.urls import include,path

app_name = 'users'

urlpatterns = [
    path('register/',view=register,name='register'),
    path('cart/',view=cart_view,name='cart_view'),
    path('add-to-cart/',view=add_to_cart,name='add_to_cart'),
    path('delete-from-cart/',view=delete_from_cart,name='delete_from_cart'),
    path('check-out/',view=check_out_view,name='check_out_view')
]