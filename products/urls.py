from django.urls import path
from .views import product_view_dummy,update_product,create_product,list_products,product_view,delete_product


app_name = 'products'

urlpatterns = [
    # path('',view=product_view_dummy,name='dummy_product_view'),
    path('update-product/<int:pk>/',view=update_product,name='update_product'),
    path('create-product/',view=create_product,name='create_product'),
    path('',view=list_products,name='list_products'),
    path('product-view/<int:pk>',view=product_view,name='product_view'),
    path('delete-product/<int:pk>',view=delete_product,name='delete_product')
]   

