from django.contrib import admin
from .models import Product,Attribute,AttributeValue,Category,ProductVariant,VariantAttributeValue,VariantImage
# Register your models here.


admin.site.register(Product)
admin.site.register(Attribute)
admin.site.register(AttributeValue)
admin.site.register(VariantAttributeValue)
admin.site.register(Category)
admin.site.register(ProductVariant)
admin.site.register(VariantImage)