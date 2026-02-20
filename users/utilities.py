from django.contrib.auth import get_user_model
from .models import Cart,CartItems
from django.core.exceptions import ValidationError
from django.db import transaction


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
def save_item_to_db(user,item_id,qty,items_count):
    cart,_ = Cart.objects.update_or_create(user=user,defaults={'products_count':items_count})

    cart_item,_ = CartItems.objects.update_or_create(cart=cart,product_variant_id=item_id,defaults={'qty':qty})

@transaction.atomic
def delete_item_from_db(user,item_id,items_count):
    cart,_ = Cart.objects.update_or_create(user=user,defaults={'products_count':items_count})

    cart_item = CartItems.objects.filter(cart=cart,product_variant_id=item_id).delete()


def get_shipping_value():
    return 350

def get_discount_value():
    return 0

def get_tax_value():
    return 0
