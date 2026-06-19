from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):

    if not isinstance(dictionary, dict):
        return ""

    key = str(key).strip()

    for k, v in dictionary.items():

        if str(k).strip() == key:
            return v

    return ""
@register.filter
def split_comma(value):
    if not value:
        return []
    return [v.strip() for v in value.split(",")]