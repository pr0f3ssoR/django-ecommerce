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