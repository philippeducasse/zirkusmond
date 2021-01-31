from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import SafeString

import markdown as md

register = template.Library()


@register.filter(is_safe=True)
@stringfilter
def markdown(value: SafeString):
    ''' convert markdown to html
    '''
    return md.markdown(value)
