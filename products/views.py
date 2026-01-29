from django.shortcuts import render
from django.http import HttpResponse,HttpRequest,JsonResponse
from .models import Product,ProductVariant,Attribute,AttributeValue,VariantAttributeValue
from django.db.models import Min
from django import forms
from django.db import transaction
from .view_forms import ProductForm,ProductVariantForm,ProductVariantFormset,AttributeForm,AttributeValueFormset,formset,AttrValueFormset,AttributeFormset
from .utilities import get_product

def product_view_dummy(request):
    return HttpResponse('Hello there')


def products_view(request):
    context = {
        'products': [

        ]
    }
    


def save_product(request:HttpRequest):
    keyboard = Product.objects.first()
    keyboard_variants_intial = ProductVariant.objects.filter(product=keyboard)
    print(keyboard_variants_intial)
    print(keyboard_variants_intial.values('pk'))
    message = 'Enter Details'

    if request.method == 'POST':
        product_form = ProductForm(request.POST,instance=keyboard)
        # variant_formset = ProductVariantFormset(request.POST,prefix='variant',initial=keyboard_variants_intial)
        variant_formset = formset(request.POST,instance=keyboard,queryset=keyboard_variants_intial)
        if product_form.is_valid() and variant_formset.is_valid():
            with transaction.atomic():
                sid = transaction.savepoint()
                product = product_form.save()
                # for form in variant_formset.forms:
                #     variant = form.save(commit=False)
                #     variant.product = product
                #     variant.full_clean()
                #     print(variant)
                forms = variant_formset.save()
                for form in forms:
                    print(form.pk)
                transaction.savepoint_rollback(sid=sid)

            message = 'Success'
        else:
            message = 'Failure'
    product_form = ProductForm(instance=keyboard)
    # variant_formset = ProductVariantFormset(prefix='variant',initial=keyboard_variants_intial)
    variant_formset = formset(queryset=keyboard_variants_intial)
    attribute_form = AttributeForm()
    attribute_value_formset = AttributeValueFormset()
    return render(request,'products/product.html',{
        'product_form':product_form,
        'variant_formset':variant_formset,
        # 'attribute_form':attribute_form,
        # 'attribute_value_formset':attribute_value_formset,
        'message':message
    })



def save_product(request:HttpRequest):
    keyboard = Product.objects.first()
    keyboard_variants_intial = ProductVariant.objects.filter(product=keyboard)
    message = 'Enter Details'

    if request.method == 'POST':
        product_form = ProductForm(request.POST,instance=keyboard)
        variant_formset = formset(request.POST,instance=keyboard)
        if product_form.is_valid() and variant_formset.is_valid():
            with transaction.atomic():
                sid = transaction.savepoint()
                product = product_form.save()
                forms = variant_formset.save()
                for form in forms:
                    print(form.pk)
                # transaction.savepoint_rollback(sid=sid)

            message = 'Success'
        else:
            message = 'Failure'
    product_form = ProductForm(instance=keyboard)
    variant_formset = formset(instance=keyboard,queryset=keyboard_variants_intial)
    return render(request,'products/product.html',{
        'product_form':product_form,
        'formset':variant_formset,
        'message':message
    })

def test(request:HttpRequest):
    initial = AttributeValue.objects.values('value').first()
    queryset = AttributeValue.objects.filter(pk='1')
    if request.method == 'POST':
        formset = AttrValueFormset(request.POST,queryset)
        if formset.is_valid():
            formset.save()

    formset = AttrValueFormset(initial=[
        {'value':'New1'},
        {'value':'New2'}

    ],queryset=queryset)

    return render(request,'products/test.html',{'formset':formset})


def attribute_value(request:HttpRequest):
    if request.method == 'POST':
        pass
    attribute_qs = Attribute.objects.all().prefetch_related('attribute_value')
    attribute_formset = AttributeFormset(queryset=attribute_qs)
    for qs in attribute_qs:
        print(qs.attribute_value.all())
    attribute_value_formsets = [AttributeValueFormset(queryset=qs.attribute_value.all(),prefix=qs.name) for qs in attribute_qs ]



    return render(request,'products/test.html',{'attribute_formset':attribute_formset,'attribute_value_formsets':attribute_value_formsets})


def json_view(request:HttpRequest):

    from .view_forms import JsonProductVariantFormset,JsonProductForm

    pk = 1

    product_dict = get_product(pk=pk)

    if request.method == 'POST':
        pass


    product_form = ProductForm(initial={
        'id':product_dict['id'],
        'title':product_dict['title'],
        'description':product_dict['description']
    })

    json_product_form = JsonProductForm(initial={
        'id':product_dict['id'],
        'title':product_dict['title'],
        'description':product_dict['description']
    })

    json_variant_formset = JsonProductVariantFormset(initial=product_dict['variants'],prefix='variant')

    return render(request,'products/test.html',{'product_form':json_product_form,'variant_formset':json_variant_formset})
    
    # product_dict = get_product(pk=pk)

    # return JsonResponse(product_dict)


    