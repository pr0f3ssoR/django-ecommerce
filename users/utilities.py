from django.contrib.auth import get_user_model
from .models import Cart,CartItems
from django.core.exceptions import ValidationError
from django.db import transaction,connection
from django.db.models import F,Prefetch,OuterRef,Subquery,Func,Value
from django.db.models.functions import Concat
from products.models import VariantAttributeValue,ProductVariant
import stripe
from pprint import pprint
from django.conf import settings
from django.http import HttpRequest


class GroupConcat(Func):
    function = 'GROUP_CONCAT'
    template = "%(function)s(%(expressions)s, ' • ')"

@transaction.atomic
def register_user(cleaned_data:dict):
    User = get_user_model()

    user_data = {
        'first_name':cleaned_data.get('first_name',''),
        'last_name':cleaned_data.get('last_name',''),
        'username':cleaned_data.get('username',''),
        'email':cleaned_data.get('email',''),
        'password':cleaned_data.get('password','')
    }

    user = User(**user_data)
    cart = Cart(user=user)
    try:
        user.full_clean()

        # Hash password before storing it in db
        user.set_password(user_data.get('password',''))

        # Store in db
        user.save()
        cart.save()

        return user,dict()
    except ValidationError as e:
        return None,e.message_dict
    
@transaction.atomic
def save_item_to_db(user,item_id,qty):
    # cart,_ = Cart.objects.update_or_create(user=user,defaults={'products_count':items_count})
    cart = Cart.objects.get(user=user)

    cart_item,_ = CartItems.objects.update_or_create(cart=cart,product_variant_id=item_id,defaults={'qty':qty})

    cart.save()

@transaction.atomic
def delete_item_from_db(user,item_id):
    # cart,_ = Cart.objects.update_or_create(user=user,defaults={'products_count':items_count})
    cart = Cart.objects.get(user=user)

    cart_item = CartItems.objects.filter(cart=cart,product_variant_id=item_id).delete()

    cart.save()


def get_shipping_value():
    return 350

def get_discount_value():
    return 0

def get_tax_value():
    return 0



def check_out_items_details(request:HttpRequest):
    vav_subquery = VariantAttributeValue.objects.select_related('attribute_value__attribute')\
    .filter(variant_id = OuterRef('product_variant_id' if request.user.is_authenticated else 'id'))\
    .values('variant_id')\
    .annotate(attributes=GroupConcat(
        Concat(
            F('attribute_value__attribute__name'),
            Value(':'),
            F('attribute_value__value')
        )
    ))\
    .values('attributes')[:1]

    if request.user.is_authenticated:
        cart_items = CartItems.objects.select_related('cart__user','product_variant__product')\
        .filter(cart__user=request.user)\
        .annotate(attributes=Subquery(vav_subquery))\
        .values('attributes',
                variant_id = F('product_variant_id'),
                title=F('product_variant__product__title'),
                price=F('product_variant__price'),
                item_qty=F('qty'),
                items_count=F('cart__products_count'),
                )
    
    else:
        variant_ids = [variant_id for variant_id in request.session['cart']]
        cart_items = ProductVariant.objects.select_related('product')\
        .filter(id__in=variant_ids)\
        .annotate(attributes = Subquery(vav_subquery))\
        .values('attributes',
                'price',
                variant_id = F('id'),
                title=F('product__title'))
        
        for item in cart_items:
            qty = request.session['cart'][str(item['variant_id'])]
            item['item_qty'] = qty

    return cart_items

