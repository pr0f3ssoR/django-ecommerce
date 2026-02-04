from django.db import models
from django.db.models import Min
# Create your models here.


class Product(models.Model):
    title = models.CharField(max_length=100)
    base_price = models.IntegerField(editable=False,default=0)
    description = models.TextField()
    base_image = models.ImageField(upload_to='images/products',editable=False,null=True,blank=True)
    in_stock = models.BooleanField(default=True,editable=False)

    def __str__(self):
        return self.title


class Attribute(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
class AttributeValue(models.Model):
    attribute = models.ForeignKey('Attribute',on_delete=models.CASCADE,related_name='attribute_value')
    value = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.attribute.name} - {self.value}'
    
    def get_attribute_name(self):
        return self.attribute.name
    
    def get_attribute_value(self):
        return self.value


class ProductVariant(models.Model):
    product = models.ForeignKey('Product',on_delete=models.CASCADE,related_name='product_variant')
    price = models.IntegerField(default=0)
    stock = models.IntegerField(default=0)


    def __str__(self):
        return f'{self.product.title} - {self.price}'
    
    def save(self,*args,**kwargs):

        super().save(*args,**kwargs)

        product = self.product

        base_price = ProductVariant.objects.filter(product=product).aggregate(min_price=(Min('price')))['min_price']

        product.base_price = base_price

        stock = ProductVariant.objects.filter(product=product,stock__gt=0).count()

        if stock <=0:
            product.in_stock = False

        else:
            product.in_stock = True

        product.save()
    

class VariantImage(models.Model):
    variant = models.ForeignKey('ProductVariant',on_delete=models.CASCADE,related_name='variant_image')
    image_url = models.ImageField(upload_to='images/products',null=True,blank=True)
    is_display_image = models.BooleanField(default=False)


    # def __str__(self):
    #     return f'{self.variant.product.title} - {self.variant.price}'
    
    def save(self,*args,**kwargs):
        if self.is_display_image:
            queryset = VariantImage.objects.filter(is_display_image=True).update(is_display_image=False)
            product = self.variant.product
            product.base_image = self.image_url
            product.save()
        super().save(*args,**kwargs)

class VariantAttributeValue(models.Model):
    variant = models.ForeignKey('ProductVariant',on_delete=models.CASCADE,related_name='variant_attribute_value')
    attribute_value = models.ForeignKey('AttributeValue',on_delete=models.CASCADE,related_name='variant_attribute_value')



class Category(models.Model):
    name = models.CharField(max_length=50)
    product = models.ForeignKey('Product',on_delete=models.CASCADE)

    def __str__(self):
        return self.name
