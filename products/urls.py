from django.urls import path
from .views import product_view_dummy,save_product,test,attribute_value,json_view


urlpatterns = [
    path('',view=product_view_dummy,name='dummy_product_view'),
    path('save-product/',view=save_product,name='save_product'),
    path('test/',view=json_view,name='test'),
    path('json/<int:pk>/',view=json_view,name='json_view')
]   

