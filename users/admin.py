from django.contrib import admin
from .models import Cart,CartItems,CustomUser,Order,OrderItems,ShippingAddress
from django.contrib.auth.admin import UserAdmin
# Register your models here.

admin.site.register(Cart)
admin.site.register(CartItems)
admin.site.register(Order)
admin.site.register(OrderItems)
admin.site.register(ShippingAddress)
admin.site.register(CustomUser,UserAdmin)
