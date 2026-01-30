from django import forms
from .models import Product,ProductVariant,Attribute,AttributeValue


# class ProductForm(forms.Form):
#     title = forms.CharField(label='Title',max_length=100)
#     price = forms.IntegerField(label='Price')
#     stock = forms.IntegerField(label='Stock')
#     image = forms.ImageField(label='Image')
    


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title','description']


class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        exclude = ['product']

class AttributeForm(forms.ModelForm):
    class Meta:
        model = Attribute
        fields = '__all__'

class AttributeValueForm(forms.ModelForm):
    class Meta:
        model = AttributeValue
        exclude = ['attribute']


class NewProductForm(forms.ModelForm):
    json_field = forms.JSONField()
    class Meta:
        model = Product
        fields = ['title','description']



ProductVariantFormset = forms.formset_factory(form=ProductVariantForm,extra=1)
AttributeValueFormset = forms.modelformset_factory(model=AttributeValue,fields=['value'])
AttributeFormset = forms.modelformset_factory(model=Attribute,fields='__all__')
formset = forms.inlineformset_factory(Product,ProductVariant,form=ProductVariantForm,extra=0,can_delete=True)

AttrValueFormset = forms.modelformset_factory(AttributeValue,exclude=['attribute'],extra=3,edit_only=True)



class JsonProductForm(forms.Form):
    id = forms.IntegerField(required=False,min_value=1,widget=forms.HiddenInput())
    title = forms.CharField(max_length=100)
    description = forms.CharField(widget=forms.Textarea())


class JsonProductVariantForm(forms.Form):
    id = forms.IntegerField(required=False,min_value=1,widget=forms.HiddenInput())
    price = forms.IntegerField(required=True,min_value=0)
    stock = forms.IntegerField(required=True,min_value=0)
    attributes = forms.JSONField()

JsonProductVariantFormset = forms.formset_factory(form=JsonProductVariantForm,extra=0)
