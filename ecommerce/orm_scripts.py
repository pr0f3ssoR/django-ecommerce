import os
import sys
import django
from django.db import connection,transaction
from django.db.models import Min,Subquery,OuterRef,F,Prefetch
from pprint import pprint

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
    )


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
    


def handle_attribute_values(variant,attribute_value_obj):
    try:
        vav_obj = VariantAttributeValue.objects.get(variant_id=variant.id,attribute_value_id=attribute_value_obj.id)
    except:
        vav_obj = VariantAttributeValue(variant=variant,attribute_value=attribute_value_obj)
        # vav_obj.save()


    

def fetch_data_from_db(product_data:dict):
    try:
        product = Product.objects.get(id=product_data['id'])
    except:
        product = Product()

    product_title = product_data['title']
    product_description = product_data['description']

    product.title = product_title
    product.description = product_description

    # product.save()

    variants = product_data['variants']

    existing_variant_ids = []

    for variant_data in variants:
        variant_id = variant_data.get('id')
        if variant_id: existing_variant_ids.append(variant_id)

    
    attribute_names_cache = dict()
    attriubte_values_cache = dict()
        
    
    variants_in_bulk = ProductVariant.objects.filter(product=product,id__in=existing_variant_ids).select_related('product').in_bulk()



    for variant_data in variants:
        variant = variants_in_bulk.get(variant_data['id']) if variant_data.get('id',None) else ProductVariant(product=product)

        variant_price = variant_data['price']
        variant_stock = variant_data['stock']

        variant.price = variant_price
        variant.stock = variant_stock

        # variant.save()

        attributes = variant_data['attributes']


        for attribute_data in attributes:
            attribute_name = attribute_data['name']
            attribute_value = attribute_data['value']

            if attribute_name not in attribute_names_cache:
                attribute_obj,is_created = Attribute.objects.get_or_create(name=attribute_name)
                attribute_names_cache[attribute_name] = attribute_obj
            else:
                attribute_obj = attribute_names_cache[attribute_name]
            
            if attribute_value not in attriubte_values_cache:
                attribute_value_obj = AttributeValue.objects.filter(attribute=attribute_obj,value=attribute_value).select_related('attribute').first()

                if not attribute_value_obj:
                    attribute_value_obj = AttributeValue(attribute=attribute_obj,value=attribute_value)
                    # attribute_value_obj.save()

                attriubte_values_cache[attribute_value] = attribute_value_obj
            
            else:
                attribute_value_obj = attriubte_values_cache[attribute_value]

            
            try:
                vav_obj = VariantAttributeValue.objects.get(variant_id=variant.id,attribute_value_id=attribute_value_obj.id)
            except:
                vav_obj = VariantAttributeValue(variant=variant,attribute_value=attribute_value_obj)
                # vav_obj.save()       


    pprint(connection.queries)
    print(f'Number of queries: {len(connection.queries)}')
        


class ProductUpsertService:
    def __init__(self,product_data):

        self.product_data = product_data

        self.attribute_cache = dict()
        self.attribute_value_cache = dict()

    # @transaction.atomic
    def execute(self):
        
        product = self._upsert_product()
        variants = self.product_data.get('variants',[])

        existing_variant_map = self._get_existing_variants(product,variants)

        for variant_data in variants:

            variant = self._upsert_variant(product,variant_data,existing_variant_map)
            variant_attributes = variant_data['attributes']

            self._handle_attributes(variant,variant_attributes)
        
        pprint(connection.queries)
        print(f'Number of queries: {len(connection.queries)}')



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


product_upsert_service = ProductUpsertService(product_data)
product_upsert_service.execute()


