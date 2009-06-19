# coding: utf-8

from django import template
from django.utils.encoding import smart_unicode
from django.utils.safestring import mark_safe

register = template.Library()

@register.inclusion_tag('filebrowser/include/_response.html', takes_context=True)
def query_string(context, add=None, remove=None):
    """
    Allows the addition and removal of query string parameters.
    
    _response.html is just {{ response }}
    
    Usage:
    http://www.url.com/{% query_string "param_to_add=value, param_to_add=value" "param_to_remove, params_to_remove" %}
    http://www.url.com/{% query_string "" "filter" %}filter={{new_filter}}
    http://www.url.com/{% query_string "sort=value" "sort" %}
    """
    # Written as an inclusion tag to simplify getting the context.
    add = string_to_dict(add)
    remove = string_to_list(remove)
    params = context['query'].copy()
    response = get_query_string(params, add, remove)
    return {'response': response }
    

def query_helper(query, add=None, remove=None):
    """
    Helper Function for use within views.
    """
    add = string_to_dict(add)
    remove = string_to_list(remove)
    params = query.copy()
    return get_query_string(params, add, remove)
    

def get_query_string(p, new_params=None, remove=None):
    """
    Add and remove query parameters. From `django.contrib.admin`.
    """
    if new_params is None: new_params = {}
    if remove is None: remove = []
    for r in remove:
        for k in p.keys():
            if k.startswith(r):
                del p[k]
    for k, v in new_params.items():
        if k in p and v is None:
            del p[k]
        elif v is not None:
            p[k] = v
    return mark_safe('?' + '&'.join([u'%s=%s' % (k, v) for k, v in p.items()]).replace(' ', '%20'))
    

def string_to_dict(string):
    """
    Usage::
    
        {{ url|thumbnail:"width=10,height=20" }}
        {{ url|thumbnail:"width=10" }}
        {{ url|thumbnail:"height=20" }}
    """
    kwargs = {}
    if string:
        string = str(string)
        if ',' not in string:
            # ensure at least one ','
            string += ','
        for arg in string.split(','):
            arg = arg.strip()
            if arg == '': continue
            kw, val = arg.split('=', 1)
            kwargs[kw] = val
    return kwargs
    

def string_to_list(string):
    """
    Usage::
    
        {{ url|thumbnail:"width,height" }}
    """
    args = []
    if string:
        string = str(string)
        if ',' not in string:
            # ensure at least one ','
            string += ','
        for arg in string.split(','):
            arg = arg.strip()
            if arg == '': continue
            args.append(arg)
    return args
    

