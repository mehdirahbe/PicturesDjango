from django import template

register = template.Library()

#allow to replace _ by / in the html templates
@register.filter(name='replace_underscore')
def replace_underscore(value):
    return value.replace('_', '/')
