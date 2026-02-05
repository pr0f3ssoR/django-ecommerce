from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse
from django.http import HttpResponse,HttpRequest,JsonResponse
from .models import Product,ProductVariant,Attribute,AttributeValue,VariantAttributeValue
from django.db.models import Min
from django import forms
from django.db import transaction
from .view_forms import ProductForm,ProductVariantForm,ProductVariantFormset
from .utilities import ProductUpsertService,ProductFetcher
from pprint import pprint

def product_view_dummy(request):
    return HttpResponse('Hello there')


def update_product(request:HttpRequest,pk):

    errors = []

    if request.method == 'POST':
        product_form = ProductVariantFormset(request.POST)
        variant_formset = ProductForm(request.POST,prefix='variant')


        if product_form.is_valid() and variant_formset.is_valid():

            product_data = product_form.cleaned_data
            variants = variant_formset.cleaned_data

            product_upsert_service = ProductUpsertService(product_data,variants)
            product_upsert_service.execute()
                

    serialized_product = ProductFetcher().get_serialized_product(product=1)


    product_form = ProductForm(initial={
        'id':serialized_product['id'],
        'title':serialized_product['title'],
        'description':serialized_product['description']
    })

    variant_formset = ProductVariantFormset(initial=serialized_product['variants'],prefix='variant')
    # for form in json_variant_formset:
    #     print(form.initial['attributes'])

    return render(request,'products/crud_product_template.html',{'product_form':product_form,'variant_formset':variant_formset,'errors':errors})
    

def create_product(request:HttpRequest):
    if request.method == 'POST':
        product_form = ProductForm(request.POST)
        variant_formset = ProductVariantFormset(request.POST,prefix='variant')

        if product_form.is_valid() and variant_formset.is_valid():
            product_upsert_service = ProductUpsertService(product_data=product_form.cleaned_data,variants=variant_formset.cleaned_data)
            product = product_upsert_service.execute()
            url = reverse('products:update_product',kwargs={'pk':product.id})
            return redirect(url)

    product_form = ProductForm()
    variant_formset = ProductVariantFormset(prefix='variant')
    return render(request,'products/crud_product_template.html',{'product_form':product_form,'variant_formset':variant_formset})

    
