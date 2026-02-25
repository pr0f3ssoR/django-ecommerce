import os
import sys
import django
from django.db import connection,transaction
from django.db.models import Min,Subquery,OuterRef,F,Prefetch,Count
from pprint import pprint
from typing import Union
from dotenv import load_dotenv

# 🔹 Add project root (where manage.py lives)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# 🔹 Django settings
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "ecommerce.settings"
)

# 🔹 Setup Django
django.setup()

from products.models import (
        Product,
        Attribute,
        AttributeValue,
        ProductVariant,
        VariantAttributeValue,
        VariantImage
    )

def test2():
    # product_variant_qs = ProductVariant.objects.select_related('product')\
    # .prefetch_related(
    #     Prefetch(
    #         'variant_attribute_value',queryset=\
    #         VariantAttributeValue.objects.select_related('attribute_value__attribute'))
    # ).filter(product_id=1)

    # print(product_variant_qs)

    # product_data = Product.objects.prefetch_related(
    #     Prefetch(
    #         'product_variant',
    #         queryset=ProductVariant.objects.prefetch_related(
    #             Prefetch(
    #                 'variant_attribute_value',
    #                 queryset=VariantAttributeValue.objects.select_related('attribute_value__attribute')
    #             )
    #         )
    #     )
    # ).get(id=1)

    # data = VariantAttributeValue.objects.select_related(
    #     'variant__product',
    #     'attribute_value__attribute'
    # ).filter(variant__product_id=1)

    # product = data

    pprint(connection.queries)
    print(f'Number of queries: {len(connection.queries)}')



def test():

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
    ).filter(product_id=1)

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
                'id':vav.id,
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
    def __init__(self,product_data):

        self.product_data = product_data

        self.attribute_cache = dict()
        self.attribute_value_cache = dict()

    # @transaction.atomic
    def execute(self):
        
        product = self._upsert_product()

        input_variants = self.product_data.get('variants',[])

        current_variant_qs = product.product_variant.all()

        existing_variant_map = self._get_variants(product,variants)

        for variant_data in variants:

            variant = self._upsert_variant(product,variant_data,existing_variant_map)
            variant_attributes = variant_data['attributes']

            self._handle_attributes(variant,variant_attributes)



    def __process_input_variants(self,input_variants,current_variants,product):
        """
        This method loops through over variants sent by user and extract dict of variants that already exist, variants that needs to be created
        and array of variant ids which needs to be deleted

        """

        input_update_variant_map = dict()
        input_create_variants = []


        for variant in input_variants:
            variant_id = variant.pop('id',None)
            attributes = variant.get('attributes',[])
            images = variant.get('images',[])

            if variant_id:
                input_update_variant_map[variant_id] = variant
            else:
                variant_obj = ProductVariant(product=product,**variant)
                input_create_variants.append(variant_obj)

            

    def __process_input_attributes(self,attributes):


        for attribute in attributes:
            attribute_vav_id = attribute.get('id',None)
            

    def _upsert_product(self):

        product_id = self.product_data['id']
        product_title = self.product_data['title']
        product_description = self.product_data['description']

        try:
            product = Product.objects.prefetch_related(
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
        except Product.DoesNotExist:
            product = Product()

        product.title = product_title
        product.description = product_description
        # product.save()

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
        # variant.save()

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
                attribute_value_obj = AttributeValue(attribute=attribute_obj,value=attribute_value_obj)
                # attribute_value_obj.save()
            self.attribute_cache[key] = attribute_value_obj
        return attribute_value_obj
        

    def _upsert_variant_attribute_value(self,variant,attribute_value_obj):
        try:
            vav_obj = VariantAttributeValue.objects.get(variant=variant,attribute_value=attribute_value_obj)
        except VariantAttributeValue.DoesNotExist:
            vav_obj = VariantAttributeValue(variant=variant,attribute_value=attribute_value_obj)
            # vav_obj.save()

            return vav_obj

        

product_data = {'id': 1, 'title': 'Keyboard', 'description': 'Simple Keyboard', 'variants': [{'id': 48, 'price': 200, 'stock': 23, 'attributes': [{'name': 'Size', 'value': 'Tkl'}, {'name': 'Connectivity', 'value': 'Wired'}]}, {'id': 49, 'price': 300, 'stock': 61, 'attributes': [{'name': 'Connectivity', 'value': 'Wireless'}, {'name': 'Size', 'value': 'Tkl'}]}]}



def why_extra_queries():
    # vav_obj = VariantAttributeValue.objects.get(variant_id=48,attribute_value_id=5)
    vav_obj = VariantAttributeValue.objects.raw('''SELECT * FROM products_variantattributevalue
                                                    where attribute_value_id = %s and variant_id = %s
                                                ''',[5,48])

    print(list(vav_obj))

    pprint(connection.queries)
    print(f'Number of queries: {len(connection.queries)}')

# why_extra_queries()
# test()
# fetch_data_from_db(product_data)


# product_upsert_service = ProductUpsertService(product_data)
# product_upsert_service.execute()

# test2()
# product = ProductFetcher().get_product(product_id=1)

# serialized_product = ProductFetcher().get_serialized_product(product=1)

def null_images():
    for img in VariantImage.objects.all(): 
        if not img.image_url:  
            img.delete()

def delete_image(pk):
    try:
        variant_image = VariantImage.objects.get(pk=pk)
        variant_image.delete()
    except VariantImage.DoesNotExist:
        pass

def test():
    variant = ProductVariant.objects.prefetch_related(Prefetch('variant_image',queryset=VariantImage.objects.only('image_url'))).first()

    print(variant.variant_image.first())


# print(product)

# product_data = ProductFetcher().get_serialized_product(product=16)

# pprint(product_data)


from users.models import CartItems



def duplicates():
    duplicate_items = CartItems.objects.values('cart','product_variant').annotate(count=Count('id')).filter(count__gt=1)

    print(duplicate_items)


def image_by_path():
    image = VariantImage.objects.filter(image_url='images/products/headphones.webp')

    print(image)

image_by_path()