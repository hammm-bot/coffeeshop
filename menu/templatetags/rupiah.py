from django import template
from django.utils.html import format_html

register = template.Library()

@register.filter
def rupiah(value):
    try:
        value = int(float(value))  # untuk handle Decimal atau float
        return format_html("Rp {:,}".format(value).replace(",", "."))
    except:
        return value
