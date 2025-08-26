from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Return dictionary[key] or None if missing."""
    if dictionary is None:
        return None
    return dictionary.get(key)

@register.filter
def get_nested(d, args):
    """
    Access nested dict values in templates.
    Usage: {{ existing_scores|get_nested:"123,technique" }}
    """
    if not d:
        return None
    keys = args.split(',')
    try:
        val = d
        for k in keys:
            if k.isdigit():
                k = int(k)
            val = val[k]
        return val
    except Exception:
        return None
