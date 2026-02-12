from django.urls import path
from .views import product_view_dummy,update_product,create_product


app_name = 'products'

urlpatterns = [
    path('',view=product_view_dummy,name='dummy_product_view'),
    path('update-product/<int:pk>/',view=update_product,name='update_product'),
    path('create-product/',view=create_product,name='create_product'),
]   

