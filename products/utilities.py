from .models import ProductVariant,VariantAttributeValue,Product,Attribute,AttributeValue
from django.db.models import Prefetch
from django.db import transaction

def get_product(pk:int) -> dict:
    
    context = {
        'id':'',
        'title':'',
        'description':'',
        'variants':[]
    }

    product_variant_qs = ProductVariant.objects.select_related('product')\
    .prefetch_related(
        Prefetch(
            'variant_attribute_value',queryset=\
            VariantAttributeValue.objects.select_related('attribute_value__attribute'))
    ).filter(product_id=pk)

    for product_variant in product_variant_qs:
        product = product_variant.product

        product_id = product.id
        product_title = product.title
        product_description = product.description

        variants_map = {
            'id':product_variant.id,
            'price':product_variant.price,
            'stock':product_variant.stock,
            'attributes':[]
        }

        for vav in product_variant.variant_attribute_value.all():
            attributes_map = dict()
            attribute_name = vav.attribute_value.attribute.name
            attribute_value = vav.attribute_value.value
            attributes_map['name'] = attribute_name
            attributes_map['value'] = attribute_value
            variants_map['attributes'].append(attributes_map)


        context['id'] = product_id
        context['title'] = product_title
        context['description'] = product_description
        context['variants'].append(variants_map)

    return context


class ProductUpsertService:
    def __init__(self,product_data,variants):

        self.product_data = product_data
        self.variants = variants

        self.attribute_cache = dict()
        self.attribute_value_cache = dict()

    @transaction.atomic
    def execute(self):
        
        product = self._upsert_product()
        variants = self.variants

        existing_variant_map = self._get_existing_variants(product,variants)

        for variant_data in variants:

            variant = self._upsert_variant(product,variant_data,existing_variant_map)
            variant_attributes = variant_data['attributes']

            self._handle_attributes(variant,variant_attributes)

    def _upsert_product(self):

        product_id = self.product_data['id']
        product_title = self.product_data['title']
        product_description = self.product_data['description']

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            product = Product()

        product.title = product_title
        product.description = product_description
        product.save()

        return product
    
    def _upsert_variant(self,product,variant_data,existing_variant_map):

        variant_id = variant_data.get('id',None)
        variant_price = variant_data['price']
        variant_stock = variant_data['stock']

        if not variant_id:
            variant = ProductVariant(product=product)
        else:
            variant = existing_variant_map.get(variant_id)
        
        variant.price = variant_price
        variant.stock = variant_stock
        variant.save()

        return variant


    def _get_existing_variants(self,product,variants):

        existing_variant_ids = []

        for variant_data in variants:
            variant_id = variant_data.get('id')
            if variant_id: existing_variant_ids.append(variant_id)

        existing_variants_map= ProductVariant.objects.filter(product=product,id__in=existing_variant_ids).select_related('product').in_bulk()

        return existing_variants_map
    

    def _handle_attributes(self,variant,attributes):

        for attribute_data in attributes:
            attribute_obj = self._get_attribute_obj(attribute_data)
            attribute_value_obj = self._get_attribute_value_obj(attribute_obj,attribute_data)

            vav_obj = self._upsert_variant_attribute_value(variant,attribute_value_obj)
            
    

    def _get_attribute_obj(self,attribute_data):
        attribute = attribute_data['name']

        if attribute in self.attribute_cache:
            attribute_obj = self.attribute_cache[attribute]
        else:
            try:
                attribute_obj = Attribute.objects.get(name=attribute)
            except Attribute.DoesNotExist:
                attribute_obj = Attribute(name=attribute)
                attribute_obj.save()
            self.attribute_cache[attribute] = attribute_obj
        
        return attribute_obj

    def _get_attribute_value_obj(self,attribute_obj,attribute_data):
        attribute_value = attribute_data['value']
        key = (attribute_obj.id,attribute_value)

        if key in self.attribute_cache:
            attribute_value_obj = self.attribute_cache[key]
        else:
            try:
                attribute_value_obj = AttributeValue.objects.select_related('attribute').get(attribute=attribute_obj,value=attribute_value)
            except AttributeValue.DoesNotExist:
                attribute_value_obj = AttributeValue(attribute=attribute_obj,value=attribute_value)
                attribute_value_obj.save()
            self.attribute_cache[key] = attribute_value_obj
        return attribute_value_obj

    def _upsert_variant_attribute_value(self,variant,attribute_value_obj):
        try:
            vav_obj = VariantAttributeValue.objects.get(variant=variant,attribute_value=attribute_value_obj)
        except VariantAttributeValue.DoesNotExist:
            vav_obj = VariantAttributeValue(variant=variant,attribute_value=attribute_value_obj)
            vav_obj.save()

            return vav_obj