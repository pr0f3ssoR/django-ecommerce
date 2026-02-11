from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse
from django.http import HttpResponse,HttpRequest,JsonResponse
from .models import Product,ProductVariant,Attribute,AttributeValue,VariantAttributeValue
from django.db.models import Min
from django import forms
from django.db import transaction
from .view_forms import ProductForm,ProductVariantForm,ProductVariantFormset,VariantImageForm,DeleteForm
from .utilities import ProductUpsertService,ProductFetcher,handle_deletion
from pprint import pprint

def product_view_dummy(request):
    return HttpResponse('Hello there')


def update_product(request:HttpRequest,pk):

    errors = []

    if request.method == 'POST':
        product_form = ProductForm(request.POST)
        variant_formset = ProductVariantFormset(request.POST,request.FILES,prefix='variant')
        delete_form = DeleteForm(request.POST)


        if product_form.is_valid() and variant_formset.is_valid() and delete_form.is_valid():
            product_data = product_form.cleaned_data
            variants_data = variant_formset.cleaned_data
            delete_form_data = delete_form.cleaned_data

            product_upsert_service = ProductUpsertService(product_data,variants_data)
            product_upsert_service.execute()

            delete_product_id = delete_form_data.get('delete_product_id',None)
            delete_variant_ids = delete_form_data.get('delete_variant_ids',[])
            delete_image_ids = delete_form_data.get('delete_image_ids',[])

            handle_deletion(delete_product_id,delete_variant_ids,delete_image_ids)

        
        else:
            pprint(variant_formset)
                

    serialized_product = ProductFetcher().get_serialized_product(product=pk)


    product_form = ProductForm(initial={
        'id':serialized_product['id'],
        'title':serialized_product['title'],
        'description':serialized_product['description']
    })


    variant_formset = ProductVariantFormset(initial=serialized_product['variants'],prefix='variant')

    delete_form = DeleteForm()

    return render(request,'products/crud_product_template.html',{'product_form':product_form,'variant_formset':variant_formset,'delete_form':delete_form,'errors':errors})
    

def create_product(request:HttpRequest):
    if request.method == 'POST':
        product_form = ProductForm(request.POST,request.FILES)
        variant_formset = ProductVariantFormset(request.POST,request.FILES,prefix='variant')

        if product_form.is_valid() and variant_formset.is_valid():
            print('Here')
            for i,form in enumerate(variant_formset):
                pprint(f"form: {i},{form.cleaned_data['image_input_field']}")
            product_upsert_service = ProductUpsertService(product_data=product_form.cleaned_data,variants=variant_formset.cleaned_data)
            product = product_upsert_service.execute()
            url = reverse('products:update_product',kwargs={'pk':product.id})
            return redirect(url)
        else:
            print('Here2')
            pprint(product_form.errors)
            pprint(variant_formset.errors)
    
    variant_image_form = VariantImageForm()

    product_form = ProductForm()
    variant_formset = ProductVariantFormset(prefix='variant')
    return render(request,'products/crud_product_template.html',{'product_form':product_form,'variant_formset':variant_formset,'variant_image_form':variant_image_form})

    

def image_upload_testing(request:HttpRequest):
    from .view_forms import ImageForm,ImageFormset

    if request.method == 'POST':
        pprint(request.FILES)
        image_formset = ImageFormset(request.POST,request.FILES)

        if image_formset.is_valid():
            # print(image_formset.cleaned_data)
            pass


        

    image_formset = ImageFormset()

    return render(request,'products/test.html',{'formset':image_formset})