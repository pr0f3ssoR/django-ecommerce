
from django.http import HttpRequest,HttpResponse
from django.shortcuts import render
from .utilities import generate_order
import stripe
from pprint import pprint

def order_success(request:HttpRequest):
    session_id = request.GET.get('session_id',None)
    
    order = None
    order_items = None
    order_summary = None

    if session_id:
        session = stripe.checkout.Session.retrieve(id=session_id,expand=['line_items','shipping_cost','customer_details'])
        
        items = [
            {'variant_id':item.metadata.get('variant_id',None),'item_qty':item.quantity}

            for item in session.line_items
        ]
        user = request.user if request.user.is_authenticated else ''

        order,order_items = generate_order(items,user)

        if hasattr(session,'customer_details'):
            pprint(session.customer_details.address)

            address_details = {
                'city':session.customer_details.address.city,
                'address1':session.customer_details.address.line1,
                'address2':session.customer_details.address.line
            }

        order_summary = {
            'sub_total':session.amount_subtotal,
            'shiiping':session.shipping_cost.amount_total if hasattr(session, 'shipping_cost') else 0,
            'total_amount':session.amount_total
        }

    
    return render(request,'users/order_success.html',context={'order_items':order_items,'order':order,'order_summary':order_summary})