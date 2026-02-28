from django.shortcuts import render,redirect
from django.http import HttpRequest,JsonResponse,HttpResponse
from .forms import RegisterForm,LoginForm
from pprint import pprint
from .utilities import register_user,get_discount_value,get_shipping_value,get_tax_value,save_item_to_db,delete_item_from_db,check_out_items_details
from .models import CartItems
from products.models import ProductVariant,VariantImage,VariantAttributeValue
from django.db.models import Prefetch
import json
import stripe
from django.conf import settings
from django.contrib.auth import authenticate,login,logout



# Create your views here.


def register_view(request:HttpRequest):
    errors = dict()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user,model_errors = register_user(form.cleaned_data)
            if not user:
                errors.update(model_errors)
            else:
                login(request,user)
                return redirect('products:list_products')
        else:
            errors.update(form.errors)
            pprint(form.errors)

    form = RegisterForm()

    return render(request,'users/register.html',{'form':form,'errors':errors})


def login_view(request:HttpRequest):
    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            credentials = {
                'username':form.cleaned_data['username'],
                'password':form.cleaned_data['password']
            }
            user = authenticate(request,**credentials)
            if user:
                login(request,user)
                return redirect('products:list_products')
    form = LoginForm()
    return render(request,'users/login.html',{'form':form})

def logout_view(request:HttpRequest):
    logout(request)
    return redirect('products:list_products')


def cart_view(request:HttpRequest):
    
    if request.user.is_anonymous:
        cart_map = request.session.get('cart',dict())
        variant_ids = [variant_id for variant_id in cart_map]
    elif request.user.is_authenticated:
        cart_items = CartItems.objects.select_related('cart__user').filter(cart__user=request.user).values('product_variant_id')
        variant_ids = [item['product_variant_id'] for item in cart_items]

    variants_bulk = ProductVariant.objects.select_related('product').prefetch_related(
        Prefetch('variant_image',queryset=VariantImage.objects.only('image_url')),
        Prefetch('variant_attribute_value',queryset=VariantAttributeValue.objects.select_related('attribute_value__attribute'))
    ).filter(id__in=variant_ids).in_bulk()

    items = []

    sub_total = 0

    for variant_id,variant in variants_bulk.items():
        if request.user.is_anonymous:
            item_qty = int(cart_map.get(str(variant.id),1))
        else:
            item_qty = CartItems.objects.get(cart__user=request.user,product_variant_id=variant_id).qty

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
            if request.user.is_anonymous:
                request.session['cart'][str(product_variant_id)] = new_qty
                request.session.modified = True

            elif request.user.is_authenticated:
                save_item_to_db(request.user,item_id,new_qty)

            return JsonResponse({'cart_item_count':request.session['cart_item_count']})

    return JsonResponse({'error':'invalid'})


def delete_from_cart(request:HttpRequest):
    if request.method == 'POST':
        json_body = json.loads(request.body)
        item_id = json_body.get('id',None)


        if item_id:
            item = request.session['cart'].pop(item_id,None) if request.user.is_anonymous else None
            if item:
                request.session['cart_item_count']-=1

            request.session.modified = True

            if request.user.is_authenticated:
                delete_item_from_db(request.user,item_id)

            return JsonResponse({'cart_item_count':request.session['cart_item_count']})
        
        return JsonResponse({'error':'invalid'})
    

def check_out_view(request:HttpRequest):
    if request.method == 'POST':
        cart_items = check_out_items_details(request)
        for item in cart_items:
            print(f'Item qty: {item['item_qty']}, Item price: {item['price']}, Unit Amount: {int(item['item_qty']) * int(item['price'])}')
        session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price_data':{
                        'currency':'pkr',
                        'product_data':{
                            'name':item['title'],
                            'description':item['attributes']
                        },
                        'unit_amount':int(item['price']) * 100,
                    },
                    'quantity':int(item['item_qty']),

                }
            for item in cart_items],
            phone_number_collection={'enabled':True},
            mode='payment',success_url='http://127.0.0.1:8000/success/session_id={CHECKOUT_SESSION_ID}',
            shipping_options=[
                            {
                                'shipping_rate_data': {
                                    'display_name': 'Standard Shipping',
                                    'type': 'fixed_amount',
                                    'fixed_amount': {
                                        'amount': get_shipping_value() * 100,  
                                        'currency': 'pkr',
                                    },
                                },
                            }],
                            metadata=[
                                {
                                    'variant_id':item['item_id'],
                                    'qty':item['item_qty']
                                }
                                for item in cart_items
                            ]
                                                )
        return redirect(session.url)
    