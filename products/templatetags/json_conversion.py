import json

from django import template

register = template.Library()


@register.filter
def json_loads(value):
    if not value:
        return []
    
    if isinstance(value,(list,dict)):
        return value
    
    try:
        return json.loads(value)
    except (TypeError,json.JSONDecodeError):
        return []
    
@register.filter
def parse_attributes(attributes):

    attributes_str = ''

    for attribute in attributes:
        name = attribute['name']
        value = attribute['value']

        attributes_str+=f'{name}: {value} • '

    return attributes_str[:-2]