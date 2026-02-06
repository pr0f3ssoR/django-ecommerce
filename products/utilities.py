from .models import ProductVariant,VariantAttributeValue,Product,Attribute,AttributeValue
from django.db.models import Prefetch
from django.db import transaction
from typing import Union

class ProductFetcher:

    def __get_product(self,product_id) -> Product:
        """
        Docstring for __get_product
        
        :param self: Description
        :param product_id: Description
        :return: Description
        :rtype: Product

        This method tries to fetch product object from db by searching using given product_id, return that object if found or raise 'DoesNotExist' exception

        """

        try:
            product_obj = Product.objects.prefetch_related(
                Prefetch(
                    'product_variant',
                    queryset=ProductVariant.objects.prefetch_related(
                        Prefetch(
                            'variant_attribute_value',
                            queryset=VariantAttributeValue.objects.select_related('attribute_value__attribute')
                        ),
                        'variant_image'
                    )
                )
            ).get(id=product_id)

            return product_obj
        except Product.DoesNotExist:
            return None
        
    def __serialize_product(self,product) -> dict:

        """

        Serialize a product instance along with its variants and variant attributes.

        ⚠️ Note:
        This method assumes the product is fetched with optimized ORM queries
        (e.g. select_related / prefetch_related) to avoid N+1 queries.

        :param product: Product model instance to serialize
        :return: Serialized product data

        """

        serialized_product = {
            'id':product.id,
            'title':product.title,
            'description':product.description
        }

        variants = product.product_variant.all()
        serialized_product['variants'] = self.__serialize_variants(variants)

        return serialized_product


    def __serialize_variants(self,variants):
        serialized_variants = []

        for variant in variants:

            serialized_variant = {
                'id': variant.id,
                'price': variant.price,
                'stock': variant.stock
            }

            variant_attribute_values = variant.variant_attribute_value.all()

            serialized_variant['attributes'] = self.__serialize_attributes(variant_attribute_values)

            variant_images = variant.variant_image.all()

            serialized_variant['images'] = self.__serialize_images(variant_images)

            serialized_variants.append(serialized_variant)
        
        return serialized_variants

    
    def __serialize_attributes(self,variant_attribute_values):
        serialized_attributes = []

        for vav in variant_attribute_values:
            attribute = vav.attribute_value.attribute.name
            attribute_value = vav.attribute_value.value

            serialized_attribute = {
                'name':attribute,
                'value':attribute_value
            }

            serialized_attributes.append(serialized_attribute)
        
        return serialized_attributes
    

    def __serialize_images(self,variant_images):
        serialized_images = []

        for image in variant_images:
            serialized_image = {
                'id':image.id,
                'url':image.image_url.url
            }

            serialized_images.append(serialized_image)
        
        return serialized_images
    

    def get_product(self,product_id:int):

        if not isinstance(product_id,int):
            raise TypeError(f'Expected int for product_id arg, got f{type(product_id)}')
        product = self.__get_product(product_id)
        return product
        
    
    def get_serialized_product(self,product: Union[Product, int]) -> dict:

        """

        This method returns serilized product by accepting product (id or product object) type int or type Product[model class].
        If type int is given then this method will first fetch product from db using id given, then it will serilize it.
        If product object is given then this will serilize that product object and will simply return it

        """

        if isinstance(product,int):
            product_obj = self.__get_product(product)
        elif isinstance(product,Product):
            product_obj = product
        else:
            raise TypeError(f"Expected Product or int for product arg, got {type(product)}")
        
        return self.__serialize_product(product_obj)


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
        
        return product

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