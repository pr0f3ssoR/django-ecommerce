from django.shortcuts import render
from django.http import HttpRequest,JsonResponse
from .forms import RegisterForm
from pprint import pprint
from .utilities import register_user,get_discount_value,get_shipping_value,get_tax_value,save_item_to_db,delete_item_from_db
from .models import CartItems
from products.models import ProductVariant,VariantImage,VariantAttributeValue
from django.db.models import Prefetch
import json



# Create your views here.


def register(request:HttpRequest):
    errors = dict()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user,model_errors = register_user(form.cleaned_data)
            if not user:
                errors.update(model_errors)
        else:
            errors.update(form.errors)
            pprint(form.errors)

    form = RegisterForm()

    return render(request,'users/register.html',{'form':form,'errors':errors})


def cart_view(request:HttpRequest):
    cart_map = request.session.get('cart',dict())

    variant_ids = [variant_id for variant_id in cart_map]

    variants_bulk = ProductVariant.objects.select_related('product').prefetch_related(
        Prefetch('variant_image',queryset=VariantImage.objects.only('image_url')),
        Prefetch('variant_attribute_value',queryset=VariantAttributeValue.objects.select_related('attribute_value__attribute'))
    ).filter(id__in=variant_ids).in_bulk()

    items = []

    sub_total = 0

    for variant_id,variant in variants_bulk.items():
        item_qty = int(cart_map.get(str(variant.id),1))

        variant_data = {
            'item_id':variant_id,
            'item_title':variant.product.title,
            'item_image':variant.variant_image.first().image_url.url,
            'item_qty':item_qty,
            'item_price':variant.price,
            'item_attributes':[{'name':vav.attribute_value.attribute.name,'value':vav.attribute_value.value} for vav in variant.variant_attribute_value.all()],
            'item_total':item_qty * variant.price
        }

        sub_total+=(variant.price) * item_qty

        items.append(variant_data)

    discount = get_discount_value()
    tax = get_tax_value()
    shipping_value = get_shipping_value()

    grand_total = sub_total - discount + shipping_value

    calculated_values = {
        'sub_total':sub_total,
        'discount':discount,
        'tax':tax,
        'shipping':shipping_value,
        'grand_total':grand_total
    }


    return render(request,'users/cart.html',{'items':items,'calculated_values':calculated_values})


def add_to_cart(request:HttpRequest):
    if request.method == 'POST':
        json_body = json.loads(request.body)
        item_id = json_body.get('id',None)
        qty = json_body.get('qty',1)

        try:
            product_variant_id = int(item_id)
            qty = int(qty)
        except:
            product_variant_id = None
            qty = 1

        if product_variant_id:
            if str(product_variant_id) not in request.session['cart']:
                request.session['cart_item_count'] = request.session['cart_item_count'] + 1

            new_qty = request.session['cart'].get(str(product_variant_id),0) + qty
            request.session['cart'][str(product_variant_id)] = new_qty
            request.session.modified = True

            if request.user.is_authenticated:
                items_count = len(request.session.get('cart'))
                save_item_to_db(request.user,item_id,new_qty,items_count)

            return JsonResponse({'cart_item_count':request.session['cart_item_count']})

    return JsonResponse({'error':'invalid'})


def delete_from_cart(request:HttpRequest):
    if request.method == 'POST':
        json_body = json.loads(request.body)
        item_id = json_body.get('id',None)


        if item_id:
            item = request.session['cart'].pop(item_id,None)
            if item:
                request.session['cart_item_count']-=1

            request.session.modified = True

            if request.user.is_authenticated:
                items_count = len(request.session.get('cart'))
                delete_item_from_db(request.user,item_id,items_count)

            return JsonResponse({'cart_item_count':request.session['cart_item_count']})
        
        return JsonResponse({'error':'invalid'})