from products.models import ProductVariant,Product,VariantImage,VariantAttributeValue
from users.models import Order,OrderItems,ShippingAddress,OrderTax
from django.db.models import Func,OuterRef,F,Value,Subquery
from django.db.models.functions import Concat,Cast
from django.db import transaction
from pprint import pprint
from django.db.models import CharField

class GroupConcat(Func):
    function = 'GROUP_CONCAT'
    template = "%(function)s(%(expressions)s, ' • ')"


class TaxGroupConcat(Func):
    function = 'GROUP_CONCAT'
    template = "%(function)s(%(expressions)s, '/')"



def get_order_details(order_id):

    vav_subquery = VariantAttributeValue.objects.select_related('attribute_value__attribute')\
    .filter(variant_id = OuterRef('item_id'))\
    .values('variant_id')\
    .annotate(attributes=GroupConcat(
        Concat(
            F('attribute_value__attribute__name'),
            Value(':'),
            F('attribute_value__value')
        )
    ))\
    .values('attributes')[:1]

    image_subquery = VariantImage.objects.filter(variant_id=OuterRef('item_id'))\
    .values('image_url')[:1]


    order_items = OrderItems.objects.filter(order_id=order_id).select_related('item__product')\
    .annotate(attributes=Subquery(vav_subquery),image=Subquery(image_subquery))\
    .values('attributes',
            'qty',
            'image',
            title=F('item__product__title'),
            price = F('item__price'),
            )
    
    return order_items



@transaction.atomic
def generate_order(items,taxes_dict:dict,user,address_details):

    order = Order(user=user)

    order_items = [OrderItems(order=order,item_id=item['variant_id'],qty=item['item_qty']) for item in items]

    order_taxes = [OrderTax(order=order,name=tax_name,value=tax_value) for tax_name,tax_value in taxes_dict.items()]

    order.save()

    OrderItems.objects.bulk_create(order_items)

    OrderTax.objects.bulk_create(order_taxes)

    shipping = ShippingAddress(order=order,**address_details)
    shipping.save()
    
    order_items_qs = get_order_details(order_id=order.pk)

    return order,order_items_qs
    



def get_tracking(order_id):

    order = Order.objects.get(invoice=order_id)

    order_items = get_order_details(order.pk)

    address_details = ShippingAddress.objects.get(order_id=order.pk)

    tax_qs = list(OrderTax.objects.filter(order_id=order_id))

    tax = sum([int(tax.value) for tax in tax_qs])

    sub_total = sum(int(item['price']) * int(item['qty']) for item in order_items)

    grand_total = tax+sub_total

    order_summary = {
        'sub_total':sub_total,
        'tax':tax_qs,
        'grand_total':grand_total
    }
    
    return order,order_items,order_summary,address_details



