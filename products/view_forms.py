from django import forms
from .models import Product,ProductVariant,Attribute,AttributeValue


class MultipleImageInput(forms.ClearableFileInput):
    allow_multiple_selected = True
    attrs = {"multiple": True}

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleImageInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result
    
class ImageForm(forms.Form):
    image = MultipleFileField()


class ProductForm(forms.Form):
    id = forms.IntegerField(required=False,min_value=1,widget=forms.HiddenInput())
    title = forms.CharField(max_length=100)
    description = forms.CharField(widget=forms.Textarea())


class ProductVariantForm(forms.Form):
    id = forms.IntegerField(required=False,min_value=1,widget=forms.HiddenInput())
    price = forms.IntegerField(required=True,min_value=0)
    stock = forms.IntegerField(required=True,min_value=0)
    attributes = forms.JSONField()
    images = forms.JSONField(required=False)
    image_input_field = MultipleFileField(required=False)

class VariantImageForm(forms.Form):
    image = forms.ImageField()

class DeleteForm(forms.Form):
    delete_image_ids = forms.JSONField(required=False)
    delete_variant_ids = forms.JSONField(required=False)


ProductVariantFormset = forms.formset_factory(form=ProductVariantForm,extra=0)


ImageFormset = forms.formset_factory(form=ImageForm,extra=2)