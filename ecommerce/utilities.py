from products.models import ProductVariant,Product,VariantImage,VariantAttributeValue
from users.models import Order,OrderItems
from django.db.models import Func,OuterRef,F,Value,Subquery
from django.db.models.functions import Concat



class GroupConcat(Func):
    function = 'GROUP_CONCAT'
    template = "%(function)s(%(expressions)s, ' • ')"

def generate_order(items,user):
    order = Order(user=user)

    order_items = [OrderItems(item_id=item['variant_id'],qty=item['item_qty']) for item in items]

    order.save()

    OrderItems.objects.bulk_create(order_items)


    order_item_ids = [order_item.id for order_item in order_items]

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

    OrderItems.objects.filter(id__in=order_item_ids).select_related('item__product')\
    .annotate(attributes=Subquery(vav_subquery),image=Subquery(image_subquery))\
    .values('attributes',
            'image',
            'qty',
            title=F('item__product_title'),
            price = F('item__price'),
            )


