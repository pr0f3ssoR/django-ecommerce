
from django.http import HttpRequest,HttpResponse
from django.shortcuts import render,redirect
from .utilities import generate_order,get_tracking
import stripe
from pprint import pprint

def order_success(request:HttpRequest):
    session_id = request.GET.get('session_id',None)
    
    order = None
    order_items = None
    order_summary = None
    address_details = None

    if session_id:
        session = stripe.checkout.Session.retrieve(id=session_id,expand=['line_items','shipping_cost','customer_details'])
        
        items = [
            {'variant_id':item.metadata.get('variant_id',None),'item_qty':item.quantity}

            for item in session.line_items
        ]
        user = request.user if request.user.is_authenticated else None

        if hasattr(session,'customer_details'):

            address_details = {
                'name':session.customer_details.name,
                'city':session.customer_details.address.city,
                'address1':session.customer_details.address.line1,
                'address2':session.customer_details.address.line2,
                'postal_code':session.customer_details.address.postal_code,
                'phone':session.customer_details.phone
            }

        shipping_tax = int(session.shipping_cost.amount_total)/100 if hasattr(session, 'shipping_cost') else 0
        taxes_dict = {
            'shipping':shipping_tax
        }

        order,order_items = generate_order(items,taxes_dict,user,address_details)

        order_summary = {
            'sub_total':session.amount_subtotal/100,
            'tax':[{'name':'shipping','value':shipping_tax}],
            'grand_total':session.amount_total/100
        }

    
    return render(request,'users/order_success.html',context={'order_items':order_items,'order':order,'order_summary':order_summary,'shipping':address_details})


def home_page_redirect(request:HttpRequest):
    return redirect('products:list_products')


def tracking_view(request:HttpRequest):
    order_id = request.GET.get('id',None)

    order = None
    order_items = None
    address_details = None
    order_summary = None

    if order_id:
        order,order_items,order_summary,address_details = get_tracking(order_id)

        return render(request,'users/order_success.html',context={'order_items':order_items,'order':order,'shipping':address_details,'order_summary':order_summary})

    return render(request,'track_order.html')


