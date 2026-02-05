from django import forms
from .models import Product,ProductVariant,Attribute,AttributeValue



class ProductForm(forms.Form):
    id = forms.IntegerField(required=False,min_value=1,widget=forms.HiddenInput())
    title = forms.CharField(max_length=100)
    description = forms.CharField(widget=forms.Textarea())


class ProductVariantForm(forms.Form):
    id = forms.IntegerField(required=False,min_value=1,widget=forms.HiddenInput())
    price = forms.IntegerField(required=True,min_value=0)
    stock = forms.IntegerField(required=True,min_value=0)
    attributes = forms.JSONField()

ProductVariantFormset = forms.formset_factory(form=ProductVariantForm,extra=0)
