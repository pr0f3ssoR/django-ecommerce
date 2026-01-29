from django.urls import path
from .views import home


urlpatterns = [
    path('',view=home,name='html_view')
]