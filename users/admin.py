from django.contrib import admin
from .models import Cart,CartItems,CustomUser
from django.contrib.auth.admin import UserAdmin
# Register your models here.

admin.site.register(Cart)
admin.site.register(CartItems)
admin.site.register(CustomUser,UserAdmin)
