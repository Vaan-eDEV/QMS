from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    if not dictionary:
        return ""
    return dictionary.get(key.lower().replace(" ", ""), "")


@register.filter
def split_comma(value):
    if not value:
        return []
    return [v.strip() for v in value.split(",")]