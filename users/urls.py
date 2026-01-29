from . import views
from django.urls import include,path



urlpatterns = [
    path('',view=views.index,name='index')
]