from django import template
from django.conf import settings


register = template.Library()



@register.simple_tag
def sub_total(price,qty):
    return int(price) * int(qty)


@register.filter
def image_url(image):
    return settings.MEDIA_URL + image