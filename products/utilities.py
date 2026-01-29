from .models import ProductVariant,VariantAttributeValue
from django.db.models import Prefetch

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