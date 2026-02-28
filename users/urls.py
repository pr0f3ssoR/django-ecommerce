from .views import register_view,cart_view,add_to_cart,delete_from_cart,check_out_view,login_view,logout_view
from django.urls import include,path

app_name = 'users'

urlpatterns = [
    path('register/',view=register_view,name='register'),
    path('login/',view=login_view,name='login'),
    path('logout/',view=logout_view,name='logout'),
    path('cart/',view=cart_view,name='cart_view'),
    path('add-to-cart/',view=add_to_cart,name='add_to_cart'),
    path('delete-from-cart/',view=delete_from_cart,name='delete_from_cart'),
    path('check-out/',view=check_out_view,name='check_out_view')
]